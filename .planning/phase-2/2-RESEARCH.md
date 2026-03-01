# Phase 2: Data & Persistence - Research

**Researched:** 2026-03-01
**Domain:** Database Migrations, State Persistence, Data Lifecycle
**Confidence:** HIGH

## <user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Migration Tooling:** Use **Alembic** for all database schema changes.
- **Environment Policy:** "Migrations Only" for all environments; remove `Base.metadata.create_all()` from startup.
- **Project Structure:** Migration scripts live in the root `/migrations/` directory.
- **Persistence Depth:** `AsyncPostgresSaver` must persist the **full `AgentState`**, including nested dicts (debate args, research findings, confidence scores).
- **State Retention:** **30-day TTL** for conversation states in the PostgreSQL checkpointer.
- **Dedicated Reporting:** Synthesized reports stored in a dedicated `Reports` table, independent of checkpointer state.
- **News Cache Expiration:** Fixed **24-hour TTL** for news summaries.
- **News Cache Cleanup:** Automated background process (e.g., `apscheduler`) integrated into FastAPI lifespan.
- **Commit Policy:** Use database-level transactions for "Success-Only Commit" logic on agent interactions.
- **Concurrency:** Reject concurrent requests to the same `thread_id` while a run is active.

### Claude's Discretion
- Specific implementation of the 30-day TTL cleanup (SQL vs. Python).
- Choice of background task library (APScheduler vs. alternatives).
- Specific configuration of the `AsyncPostgresSaver` serializer.
- Pattern for cross-node transaction management.

### Deferred Ideas (OUT OF SCOPE)
- Real-time database replication or sharding.
- Multi-region persistence.
- WebSocket-based state syncing (SSE is the chosen protocol).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-012 | Use `AsyncPostgresSaver` with Railway to persist conversation threads and agent states. | Confirmed `AsyncPostgresSaver` with `JsonPlusSerializer(pickle_fallback=True)` handles full state. |
| REQ-020 | Transition from local SQLite to cloud-hosted Railway (PostgreSQL). | Alembic async setup and `AsyncPostgresSaver` are standard for this transition. |
| REQ-023 | Refactor existing models for PostgreSQL schema mapping. | Alembic migrations and SQLAlchemy 2.0 async patterns identified. |
</phase_requirements>

## Summary

Phase 2 focuses on establishing a robust, production-ready persistence layer using PostgreSQL and Alembic. The core challenge is balancing LangGraph's automatic state checkpointing with application-specific data integrity (Success-Only Commits) and lifecycle management (TTLs).

**Primary recommendation:** Use **Alembic's async template** for migrations, **APScheduler** for background cleanup, and the **"Propose-Commit" pattern** in LangGraph to ensure external database writes (like Reports) only happen upon successful graph completion.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Alembic | 1.13+ | Schema Migrations | Industry standard for SQLAlchemy; has native async support. |
| LangGraph | 0.2+ | State Persistence | `AsyncPostgresSaver` is the "blessed" checkpointer for PostgreSQL. |
| SQLAlchemy | 2.0+ | ORM / DB Toolkit | Modern async API is standard for FastAPI. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| APScheduler | 3.10+ | Background Tasks | Best for simple, in-process cron jobs like TTL cleanup. |
| Psycopg | 3.1+ | DB Driver | Required by `AsyncPostgresSaver` for high-performance async Postgres. |

**Installation:**
```bash
pip install alembic sqlalchemy psycopg[binary] langgraph apscheduler
```

## Architecture Patterns

### Recommended Project Structure
```
migrations/          # Alembic migration scripts (ROOT)
src/
├── database/
│   ├── models.py    # SQLAlchemy models
│   └── session.py   # Async engine and sessionmaker
├── lifecycle/
│   └── tasks.py     # Background cleanup tasks (TTL)
└── graph/
    └── persistence.py # AsyncPostgresSaver setup
```

### Pattern 1: Alembic Async Setup
Use the built-in `async` template to handle the event loop correctly.
```bash
# Initialize in root
alembic init -t async migrations
```
**Key `env.py` modification:**
```python
# Source: SQLAlchemy 2.0 Official Docs
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()
```

### Pattern 2: "Propose-Commit" (Success-Only Commit)
To ensure database writes (like reports) only happen if the agent succeeds, avoid writing inside intermediate nodes.
1. **Intermediate Nodes:** Add data to `state["pending_report"]`.
2. **Final Node:** A dedicated `commit_node` reads `pending_report` and writes it to the DB in a single transaction.
3. **Benefit:** If the graph fails or is interrupted before the final node, no partial data is written to the primary DB tables.

### Anti-Patterns to Avoid
- **Hand-rolling TTL:** Don't build custom Python logic to iterate over rows and delete them. Use set-based SQL deletes.
- **LLMs inside DB Transactions:** Never open a DB transaction, then call an LLM. The transaction will hang, locking rows and exhausting the pool.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| State Serialization | Manual JSON/Pickle | `JsonPlusSerializer` | Handles LangChain primitives (AIMessage, etc.) automatically. |
| Async Migration Runner | Custom script | `alembic init -t async` | Handles complex `run_sync` wrapping of sync Alembic commands. |
| Distributed Locks | Custom flag | `redis-lock` (if scaling) | Prevents multiple workers from running the same cleanup task. |

## Common Pitfalls

### Pitfall 1: Orphaned Checkpoint Blobs
**What goes wrong:** Deleting from `checkpoints` leaves data in `checkpoint_blobs` and `checkpoint_writes`.
**How to avoid:** Use a cascading delete or a multi-step SQL cleanup script that targets all three tables.
**Warning signs:** Database size increasing rapidly despite TTL implementation.

### Pitfall 2: Alembic Directory mismatch
**What goes wrong:** Alembic defaults to `./alembic`. The project requires `./migrations`.
**How to avoid:** Update `alembic.ini` to set `script_location = migrations`.

### Pitfall 3: Serializing Custom Objects
**What goes wrong:** `JsonPlusSerializer` fails on custom Python classes.
**How to avoid:** Configure `AsyncPostgresSaver` with `serde=JsonPlusSerializer(pickle_fallback=True)` or ensure all custom state objects inherit from `pydantic.BaseModel`.

## Code Examples

### 30-Day TTL Cleanup Task
```python
# Source: Verified LangGraph Postgres Patterns
async def cleanup_checkpoints(conn_string: str):
    async with await psycopg.AsyncConnection.connect(conn_string) as conn:
        async with conn.cursor() as cur:
            # Delete checkpoints older than 30 days
            await cur.execute(
                "DELETE FROM checkpoints WHERE ts < (NOW() - INTERVAL '30 days')"
            )
            # Clean up orphaned writes/blobs
            await cur.execute("""
                DELETE FROM checkpoint_writes WHERE thread_id NOT IN (SELECT thread_id FROM checkpoints);
                DELETE FROM checkpoint_blobs WHERE thread_id NOT IN (SELECT thread_id FROM checkpoints);
            """)
            await conn.commit()
```

### FastAPI Lifespan + APScheduler
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_checkpoints, CronTrigger(hour=2, minute=0), args=[settings.DATABASE_URL])
    scheduler.start()
    yield
    scheduler.shutdown()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `create_all()` | Alembic Migrations | SQLAlchemy 2.0 | Versioned, reversible schema changes. |
| Sync DB Drivers | Async Drivers (Psycopg 3) | FastAPI Era | Higher concurrency for agentic workflows. |
| Manual State Saving | LangGraph Checkpointers | LangGraph 0.1+ | Built-in "Time Travel" and persistence. |

## Open Questions

1. **Railway Deployment Tunnels:**
   - What we know: Railway supports direct TCP for migrations.
   - What's unclear: Does the Railway GitHub Action automatically run migrations?
   - Recommendation: Add a `predeploy` or `start` command in `railway.json` to run `alembic upgrade head`.

## Sources

### Primary (HIGH confidence)
- **Alembic Docs:** [Async migrations guide](https://alembic.sqlalchemy.org/en/latest/cookbook.html#asyncio-support)
- **LangGraph Docs:** [Persistence & Checkpointers](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- **SQLAlchemy 2.0:** [Asyncio support](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Secondary (MEDIUM confidence)
- **APScheduler:** Verified FastAPI integration patterns.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries are mature and standard.
- Architecture: HIGH - Propose-Commit is the recommended way for LangGraph side-effects.
- Pitfalls: MEDIUM - Specific Railway behavior with Alembic needs verification during implementation.

**Research date:** 2026-03-01
**Valid until:** 2026-04-01
