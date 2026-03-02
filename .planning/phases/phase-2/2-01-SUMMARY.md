# Plan Summary - Phase 2-01: Schema Foundation & Migrations

## Implementation Summary
Successfully established the asynchronous database migration framework using Alembic and finalized the core schema for the StockPlanner API.

- **Alembic Initialization:** Configured Alembic with the `async` template to support SQLAlchemy 2.0's non-blocking connections, resolving compatibility with Railway PostgreSQL.
- **Model Refactoring:** Added the dedicated `Report` model for permanent storage of synthesized analysis and ensured `Text` fields were used for potentially large strings (like news summaries).
- **Migration Generation:** Generated and applied the initial baseline migration (`c120f7f7bb69`), moving the project from ephemeral SQLite to persistent, version-controlled PostgreSQL schemas.
- **Lifespan Cleanup:** Removed the legacy `Base.metadata.create_all` from `src/main.py`, fully delegating database schema management to the new Alembic workflow.

## File Changes
- `alembic.ini`: Basic configuration for the migration tool.
- `migrations/env.py`: Customized to load our specific `DeclarativeBase` and `DATABASE_URL` via our `Settings` class, ensuring async compatibility.
- `migrations/versions/c120f7f7bb69_initial_schema.py`: The generated migration script containing all current models.
- `src/database/models.py`: Added the `Report` table to fulfill the persistent reporting requirement.
- `src/main.py`: Removed the legacy table auto-creation logic from the lifespan manager.
- `requirements.txt`: Added `alembic` and `greenlet` to support async migrations.

## Technical Decisions
- **Async Alembic:** We utilized `alembic init -t async` to guarantee that all migrations are non-blocking, maintaining the integrity of our FastAPI architecture.
- **Explicit Migrations Only:** We opted for a strict "Migrations Only" policy across all environments (including local dev) to prevent schema drift between developers and the Railway production database.
- **Greenlet Workaround:** `greenlet` was introduced as a dependency, which is a known requirement when bridging SQLAlchemy 2.0's async event loop with Alembic's synchronous core.

## Verification
- `alembic upgrade head` executed successfully against the database.
- `alembic current` confirms the database is at the latest revision.
- `src/main.py` starts without attempting to recreate existing tables.
