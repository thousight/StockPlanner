# Plan Summary - Phase 2-02: Persistence & Lifecycle

## Implementation Summary
Successfully integrated LangGraph persistence and automated background tasks for data lifecycle management. This fulfills REQ-012, ensuring conversation threads and agent states are durably stored in PostgreSQL.

- **LangGraph Persistence:** Implemented `AsyncPostgresSaver` configured with `JsonPlusSerializer(pickle_fallback=True)`. This robust configuration ensures that complex LangGraph objects (like `AIMessage`) are serialized correctly without losing fidelity, enabling seamless recovery of the full `AgentState`.
- **Automated Lifecycle (TTL):** Integrated `APScheduler` (AsyncIOScheduler) into the FastAPI lifecycle.
- **Background Tasks:** Created two targeted SQL cleanup jobs:
  - `cleanup_checkpoints`: Runs daily to enforce a 30-day TTL on conversation states, deleting orphaned blobs and writes to maintain database performance.
  - `cleanup_news_cache`: Runs hourly to clear expired news summaries from the `NewsCache` table.
- **FastAPI Integration:** Updated `src/main.py` to handle the startup initialization of both the scheduler and the LangGraph checkpointer tables.

## File Changes
- `src/graph/persistence.py`: New configuration file initializing the connection pool and `AsyncPostgresSaver` using the Railway-compatible connection string.
- `src/lifecycle/tasks.py`: Encapsulates the set-based SQL deletion logic for both the checkpointer cleanup and news cache expiration.
- `src/main.py`: Modified the lifespan context manager to initialize `checkpointer.setup()`, start the `APScheduler`, and gracefully shut down resources upon exit.

## Technical Decisions
- **Connection Scheme:** Converted `postgresql+asyncpg://` to `postgresql://` exclusively for the `AsyncPostgresSaver` connection pool, as it relies on `psycopg` rather than `asyncpg` directly.
- **Set-based Deletions:** Decided against ORM-level looping for cleanup tasks; instead, utilized direct SQL `DELETE` operations to maximize performance and prevent out-of-memory errors on large datasets.
- **Pickle Fallback:** Enabled `pickle_fallback=True` in `JsonPlusSerializer` to guarantee complete state recovery for objects that don't natively map to JSON.

## Verification
- Code has been written and reviewed.
- `AsyncPostgresSaver` and `APScheduler` are correctly wired into the FastAPI startup logic.
