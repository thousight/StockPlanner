# Phase 13: History Management - Research

**Researched:** 2026-03-03
**Domain:** Relational Database Persistence & Conversation History Management
**Confidence:** HIGH

## Summary

This phase focuses on transitioning conversation history from transient LangGraph state (Redis) to a permanent relational schema in PostgreSQL. This allows for efficient retrieval, management APIs (soft-deletion), and improved UI performance through cursor-based pagination.

**Primary recommendation:** Use a `chat_messages` table with UUIDv7 IDs to enable efficient keyset pagination and implement a background synchronization task that promotes the final User/AI exchange to PostgreSQL after each LangGraph completion.

<user_constraints>
## User Constraints (from 13-CONTEXT.md)

### Locked Decisions
- **Message Scope:** Store only the final messages exchanged between the User and the AI. Internal agent thoughts, tool outputs, and intermediate reasoning steps remain transient in Redis.
- **Role Mapping:** Simplify all agent outputs to the role of **"AI"**. User inputs are labeled as **"Human"**.
- **Metadata:** No structured metadata or token usage metrics will be stored in the relational table for this phase.
- **Persistence:** Use a `chat_messages` table in PostgreSQL with standard text content and timestamps.
- **Trigger:** Synchronization occurs asynchronously as a FastAPI **Background Task** triggered immediately after the LangGraph response completes.
- **Content Integrity:** Only successfully completed exchanges are promoted to permanent storage.
- **Revision Handling:** In scenarios where agents perform multiple revisions, only the **final version** presented to the user is persisted.
- **Data Backfill:** The system will attempt to backfill history for existing threads that currently reside only in Redis/Postgres checkpointer state during the first interaction after this feature is deployed.
- **Sorting:** History retrieval will return messages in **Reverse Chronological** order (newest first).
- **Pagination:** Implement **Cursor-based pagination** to optimize for mobile infinite scrolling performance.
- **Deletion:** Deleting a thread or message will perform a **Soft Delete** only, preserving the underlying data for the standard retention period (as defined in Milestone 2).
- **Scope:** Retrieval is strictly **Thread-based**; global search across all threads is not required for this phase.
- **Ownership:** Every message record must be strictly linked to a `user_id` and `thread_id`.
- **Enforcement:** Standard "Stealth 404" logic applies to unauthorized attempts to retrieve history for a thread the user does not own.

### Claude's Discretion
- [None listed - follow the goal of permanent history storage and management APIs.]

### Deferred Ideas (OUT OF SCOPE)
- Structured metadata/metrics storage in the relational table.
- Global search across all threads.
- Token usage tracking in PostgreSQL.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-080 | **Relational Message Schema**: Implement a `chat_messages` table in PostgreSQL. | Proposed SQLAlchemy model using UUIDv7 for efficient indexing and pagination. |
| REQ-081 | **Dual-Write Synchronization**: Ensure final user-AI exchange is saved upon completion. | Background task pattern researched, leveraging `AgentState["output"]` from the Summarizer agent. |
| REQ-082 | **Message Ownership**: Enforce strict user ownership of message history. | Multi-tenant filtering using `user_id` and "Stealth 404" pattern. |
| REQ-090 | **List Conversation History**: Endpoint to retrieve paginated history for a thread. | Cursor-based pagination logic using `ChatMessage.id` with `tuple_` or simple inequality filters. |
| REQ-091 | **Delete Message/Thread**: Endpoints to remove specific messages or threads. | Soft-delete implementation using `deleted_at` timestamp. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy | 2.0+ | Database ORM | Existing standard in project; supports `AsyncSession` and `tuple_` comparisons for keyset pagination. |
| uuid-utils | latest | UUIDv7 generation | Used in `User` model; provides time-ordered unique IDs perfect for cursors. |
| FastAPI | latest | Background Tasks | Built-in support for non-blocking post-response work. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| LangGraph | latest | State Retrieval | Used during background sync and backfill to fetch messages from Redis. |

**Installation:**
Already present in `requirements.txt`.

## Architecture Patterns

### Recommended Model Structure
```python
class MessageRole(str, enum.Enum):
    HUMAN = "Human"
    AI = "AI"

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid7.uuid7()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    thread_id = Column(String, ForeignKey("chat_threads.id"), index=True, nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_chat_messages_thread_pagination", "thread_id", "id"),
    )
```

### Pattern 1: Keyset Pagination (Cursor-based)
**What:** Using the `id` (UUIDv7) of the last message to fetch the next page.
**When to use:** Infinite scrolling in chat UI.
**Example:**
```python
from sqlalchemy import select, desc

# Newest first
stmt = select(ChatMessage).where(
    ChatMessage.thread_id == thread_id,
    ChatMessage.user_id == user_id,
    ChatMessage.deleted_at == None
).order_by(desc(ChatMessage.id)).limit(page_size + 1)

if last_id:
    # Since UUIDv7 is time-ordered, id < last_id fetches older messages
    stmt = stmt.where(ChatMessage.id < last_id)
```

### Anti-Patterns to Avoid
- **Offset Pagination:** `OFFSET 100` is slow for large histories and causes skipped/duplicate items if messages are added during scrolling.
- **Parsing Tool Messages:** Don't promote tool outputs or agent internal thoughts to `chat_messages`. Stick to `AgentState["user_input"]` and `AgentState["output"]`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pagination | Custom Offset Logic | Keyset Pagination | Performance and consistency with infinite scroll. |
| Unique IDs | Random UUIDv4 | UUIDv7 | Enables time-ordering without a separate composite index on `created_at`. |
| Syncing | Sync in request loop | FastAPI BackgroundTasks | Keeps response latency low; the UI can see the answer immediately while DB syncs. |

## Common Pitfalls

### Pitfall 1: Backfill Race Condition
**What goes wrong:** Multiple requests to the same thread could trigger concurrent backfill operations, leading to duplicate records.
**How to avoid:** Check if `chat_messages` count is 0 inside a database transaction or use a unique constraint on `(thread_id, langchain_id)` if you store the original LangChain IDs.
**Simplified solution:** Check existence before the backfill loop or just accept that "on-the-fly" backfill should only happen once on the first history load.

### Pitfall 2: Lost Updates in Soft Delete
**What goes wrong:** Concurrent soft-deletes or updates to `ChatThread` status.
**How to avoid:** Use standard SQLAlchemy `update()` or ensure the ownership check is always part of the `where` clause.

## Code Examples

### Background Sync Logic
```python
async def sync_chat_history_task(user_id: str, thread_id: str):
    async with get_checkpointer() as checkpointer:
        graph = create_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}
        state = await graph.aget_state(config)
        
        if not state.values or not state.values.get("output"):
            return

        async with get_db_context() as db:
            # Check for existing message to avoid duplicates from retries
            # (Simplification: just add if user_input and output exist)
            human_msg = ChatMessage(
                user_id=user_id,
                thread_id=thread_id,
                role=MessageRole.HUMAN,
                content=state.values["user_input"]
            )
            ai_msg = ChatMessage(
                user_id=user_id,
                thread_id=thread_id,
                role=MessageRole.AI,
                content=state.values["output"]
            )
            db.add_all([human_msg, ai_msg])
            await db.commit()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| PostgreSQL Checkpointer | Redis Checkpointer | Phase 12 | Faster state access, transient memory. |
| Reading history from Redis | Reading from `chat_messages` | Phase 13 | Faster UI load, permanent logs, management APIs. |

## Open Questions

1. **Duplicate Prevention during Backfill:**
   - What we know: LangGraph messages have internal IDs.
   - What's unclear: If we should store these IDs in `chat_messages` to prevent duplicates if backfill is triggered multiple times.
   - Recommendation: Add a `langchain_msg_id` (String, nullable) column to `chat_messages` with a unique constraint on `(thread_id, langchain_msg_id)` for robust deduplication.

## Sources

### Primary (HIGH confidence)
- `src/database/models.py` - Verified existing schema and `uuid7` usage.
- `src/controllers/threads.py` - Reviewed current history implementation (Redis-based).
- `13-CONTEXT.md` - Verified all decisions.

### Secondary (MEDIUM confidence)
- SQLAlchemy 2.0 Docs - Verified Keyset Pagination patterns using `tuple_` and `desc`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Standard libraries used in the project.
- Architecture: HIGH - Follows project's existing background task and repository-like patterns.
- Pitfalls: MEDIUM - Backfill race conditions are a known challenge but solvable.

**Research date:** 2026-03-03
**Valid until:** 2026-04-02
