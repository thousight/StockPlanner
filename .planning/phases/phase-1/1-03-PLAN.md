---
phase: phase-1
plan: 1-03
type: execute
wave: 3
depends_on: [1-02]
files_modified: [src/database/session.py, src/database/models.py, src/api/controllers/health.py, src/api/schemas/health.py, src/main.py]
autonomous: true
requirements: [REQ-002, REQ-003, REQ-023]
user_setup: []

must_haves:
  truths:
    - "/health endpoint returns 200 with database status 'connected'"
    - "SQLAlchemy models use the new Base and are compatible with PostgreSQL"
  artifacts:
    - path: "src/database/session.py"
      provides: "Async database engine and sessionmaker"
    - path: "src/database/models.py"
      provides: "PostgreSQL-ready SQLAlchemy models"
    - path: "src/api/controllers/health.py"
      provides: "Health check diagnostics"
  key_links:
    - from: "src/api/controllers/health.py"
      to: "src/database/session.py"
      via: "get_db dependency"
      pattern: "Depends\(get_db\)"
    - from: "src/main.py"
      to: "src/database/session.py"
      via: "lifespan engine disposal"
      pattern: "await engine\.dispose\(\)"
---

<objective>
Implement asynchronous database connectivity and health monitoring diagnostics.

Purpose: Provide a reliable way to check system health and interact with the cloud database.
Output: Async database integration and functional health endpoints.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phase-1/1-CONTEXT.md
@.planning/phase-1/1-RESEARCH.md
@.planning/phase-1/phase-1-1-02-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Async Database Session & Models</name>
  <files>src/database/session.py, src/database/models.py, src/main.py</files>
  <action>
    1. Create `src/database/session.py` (replacing/renaming `database.py`):
       - Setup `create_async_engine` using `DATABASE_URL` from config.
       - Setup `async_sessionmaker` with `expire_on_commit=False`.
       - Define `get_db` async generator for dependency injection.
       - Refer to "Async Database Dependency" in `1-RESEARCH.md`.
    2. Refactor `src/database/models.py`:
       - Use a centralized `Base = declarative_base()` or similar.
       - Ensure all column types are compatible with PostgreSQL (standard types like String, Integer, Float, DateTime are fine).
       - Remove any SQLite-specific `connect_args`.
    3. Update `src/main.py` lifespan:
       - Add `async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)` for MVP table creation.
       - Add `await engine.dispose()` on shutdown.
  </action>
  <verify>Check that `src/database/session.py` uses `async_sessionmaker` and `src/database/models.py` imports its Base correctly.</verify>
  <done>Database layer is now fully asynchronous and PostgreSQL-ready.</done>
</task>

<task type="auto">
  <name>Task 2: Health Controller & Schemas</name>
  <files>src/api/controllers/health.py, src/api/schemas/health.py, src/main.py</files>
  <action>
    1. Create `src/api/schemas/health.py`:
       - Define `HealthResponse` pydantic model with `status` (str) and `database` (str).
    2. Create `src/api/controllers/health.py`:
       - Define `GET /health` endpoint.
       - Check database connectivity by executing a simple query (e.g., `SELECT 1`).
       - Return `HealthResponse`.
    3. Register the health router in `src/main.py`.
  </action>
  <verify>Call `GET /health` and verify it returns `{"status": "ok", "database": "connected"}` (assuming a valid DATABASE_URL is provided).</verify>
  <done>Health check diagnostics are implemented and registered.</done>
</task>

</tasks>

<verification>
Verify the full flow: Start the app, hit `/health`, and confirm it connects to a (mocked or real) PostgreSQL instance. Check the table creation logs on startup.
</verification>

<success_criteria>
- `/health` endpoint correctly reports database status.
- Database operations use `AsyncSession`.
- Tables are automatically created on startup (MVP requirement).
</success_criteria>

<output>
After completion, create `.planning/phases/phase-1/phase-1-1-03-SUMMARY.md`
</output>
