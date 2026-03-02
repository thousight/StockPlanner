# Context - Phase 2: Data & Persistence

This document captures implementation decisions for Phase 2 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Migration Management (Alembic)
- **Tooling:** Use **Alembic** for all database schema changes.
- **Environment Policy:** "Migrations Only" for all environments, including local development. `Base.metadata.create_all()` should be removed from the main application startup.
- **Project Structure:** Migration scripts will live in the root `/migrations/` directory.
- **Trigger:** Migrations will be managed via the standard **Alembic CLI**.

## 2. State Persistence & Granularity
- **Persistence Depth:** The LangGraph checkpointer (`AsyncPostgresSaver`) must persist the **full `AgentState`**, including internal debate arguments, research findings, and confidence scores.
- **State Retention:** Implement a **30-day TTL** for conversation states within the PostgreSQL checkpointer.
- **Reporting:** Final synthesized reports will be stored in a **dedicated `Reports` table** for permanent retrieval and querying, independent of the checkpointer state.
- **Persistence Frequency:** State will be saved at the **node-level only**; individual tool calls or intermediate steps within a node do not need to be persisted to the checkpointer.

## 3. Data Lifecycle (News Cache)
- **Expiration:** Implement a **fixed 24-hour TTL** for all news summaries in the `NewsCache`.
- **Cleanup:** Handle expired cache entries using an **automated background process** (e.g., `apscheduler`) integrated into the FastAPI lifespan.
- **Usage Policy:** Agents should **prefer the cache** if a fresh summary exists for a given URL/ticker.
- **Storage Depth:** Persist **LLM-generated summaries only** to minimize database bloat; raw news snippets will be discarded after summarization.

## 4. Transaction & State Integrity
- **Node Failures:** The graph should implement **auto-retry** logic for individual node failures (e.g., LLM timeouts).
- **Commit Policy:** Use database-level transactions to ensure agent interactions and state updates are only committed upon **successful node completion** (Success-Only Commit).
- **Concurrency:** The API will **reject concurrent requests** to the same `thread_id` while a run is active.
- **Error Handling:** If a run ultimately fails after retries, the API must return an **explicit error message** to the Flutter client, including any partial results available.
