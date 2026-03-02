# Phase 5: Agentic Flow Refinement - Research

**Researched:** 2024-05-24
**Domain:** Agentic Workflow, PostgreSQL Search, LangGraph Interrupts, SSE
**Confidence:** HIGH

## Summary
This research defines the implementation strategy for refined agentic flows, focusing on safety interrupts, complexity thresholding, and optimized report management. The core findings recommend using PostgreSQL's native full-text search capabilities via stored generated columns for efficiency, and a heuristic-based complexity model using linguistic metrics to gate human-in-the-loop (HITL) interrupts.

**Primary recommendation:** Use a "Dual-Gating" logic for interrupts where keyword detection (P0) and complexity heuristics (P1) determine if a report requires manual approval before being committed to the database.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Unified Topic Field:** Replace/augment `symbol` with a high-level topic (e.g., "Seattle Housing").
- **Categorization:** Explicit categories (STOCK, REAL_ESTATE, MACRO, FUND, GENERAL).
- **Presentation:** Reports must include a `Title` field.
- **Off-Topic Exclusion:** "Off-Topic" agent results do not generate reports.
- **Strict Approval Policy:** All report generation triggers a safety interrupt by default.
- **Threshold Gating:** Simple/short responses bypass interrupts via "Threshold Check".
- **Action Overrides:** Keywords like BUY, SELL, TRADE force interrupts regardless of complexity.
- **Interrupt Payload:** Must include Title, Topic, and Category.
- **Filtering & Search:** Support category filtering and keyword search.
- **Auto-Tagging:** 2-3 tags per report.
- **Thread Linkage:** Maintain `thread_id` in reports.

### Claude's Discretion
- Implementation of the complexity threshold logic.
- Structure of the SSE payload for interrupts and silent updates.
- Graph routing for "Acknowledge & Continue" pattern.

### Deferred Ideas (OUT OF SCOPE)
- Animations for UI.
- Direct execution of trades.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-011 | LangGraph Orchestration | Validated `astream_events` v2 for interrupt delivery and `Command(resume=...)` for feedback. |
| REQ-013 | Thread Management | Confirmed `thread_id` linkage in reports and checkpoint persistence for resume operations. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sqlalchemy` | 2.0+ | ORM | Supports `Computed` columns for Postgres FTS. |
| `textstat` | Latest | Complexity Heuristics | Industry standard for readability metrics. |
| `spacy` | 3.7+ | Structural Analysis | Best-in-class dependency parsing for tree depth. |
| `langgraph` | Latest | Agent Orchestration | Native support for interrupts and state persistence. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|--------------|
| `asyncpg` | Latest | DB Driver | Required for async FastAPI/SQLAlchemy operations. |

## Architecture Patterns

### PostgreSQL Keyword Search (GIN + tsvector)
To implement efficient search across `Title`, `Topic`, and `Content`, use a **Stored Generated Column**. This ensures the index is always in sync and pre-computed.

```python
# Model Definition
search_vector = Column(
    TSVECTOR,
    Computed(
        "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(topic, '') || ' ' || coalesce(content, ''))",
        persisted=True
    )
)
__table_args__ = (Index("ix_report_search_vector", search_vector, postgresql_using="gin"),)
```

### Complexity Threshold Logic
The "Threshold Check" will combine **Readability** and **Structural Depth**:
1. **P0 (Mandatory):** If content contains [BUY, SELL, TRADE], `is_complex = True`.
2. **P1 (Linguistic):** Calculate `flesch_reading_ease` (Lower is harder) and `max_dependency_depth`.
3. **Threshold:** `is_complex = (flesch < 50) OR (depth > 5)`.

### Acknowledge & Continue Pattern
When a user rejects a commit (via `Command(resume={"action": "reject"})`):
1. The graph resumes at the `commit` node's entry (due to `interrupt_before`).
2. The logic checks the resume value.
3. If "reject", it updates state with `status="REJECTED"` and routes to a `rejection_handler` node.
4. The `rejection_handler` emits a final summary/ack message and ends the turn without calling the DB write logic.

## SSE Payload Structure

### Interrupt Payload (v2 astream_events)
Surfaced under `on_chain_stream` -> `data.chunk.__interrupt__`.

```json
{
  "event": "on_chain_stream",
  "data": {
    "chunk": {
      "__interrupt__": [{
        "id": "...",
        "value": {
          "title": "NVIDIA Q4 Analysis",
          "topic": "NVDA",
          "category": "STOCK",
          "message": "Verify results before committing."
        }
      }]
    }
  }
}
```

### Silent Update Event
A custom SSE event type to trigger client-side background refreshes.
```text
event: update
data: {"type": "REPORT_COMMITTED", "thread_id": "...", "report_id": 123}
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Readability Metrics | Custom regex | `textstat` | Handles edge cases in syllables and sentence structure. |
| Full-Text Search | `ILIKE %query%` | Postgres `tsvector` | Scalability and support for stemming/ranking. |
| Graph State Management | Global variables | LangGraph Checkpointers | Thread safety and persistence. |

## Common Pitfalls

### Pitfall 1: NULL concatenation in FTS
**What goes wrong:** `title || content` returns `NULL` if either is `NULL`.
**How to avoid:** Always use `coalesce(column, '')` in the `Computed` expression.

### Pitfall 2: Blocking Async Loop
**What goes wrong:** `spacy.load()` or complex parsing blocks the event loop.
**How to avoid:** Load the spaCy model once at startup and run the threshold check in a thread pool if processing very large reports.
