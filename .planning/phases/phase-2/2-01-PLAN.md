---
phase: phase-2
plan: 2-01
type: execute
wave: 1
depends_on: []
files_modified: [alembic.ini, migrations/env.py, src/database/models.py, src/main.py]
autonomous: true
requirements: [REQ-020, REQ-023]
user_setup: []
must_haves:
  truths:
    - "Database tables are created via Alembic migrations, not app startup"
    - "The Reports table exists in the PostgreSQL schema"
    - "Migrations can be run asynchronously via Alembic CLI"
  artifacts:
    - path: "alembic.ini"
      provides: "Migration configuration"
    - path: "migrations/env.py"
      provides: "Async migration runner"
    - path: "src/database/models.py"
      provides: "Updated SQL models"
  key_links:
    - from: "migrations/env.py"
      to: "src/database/models.py"
      via: "target_metadata import"
      pattern: "from src.database.models import Base"
---

<objective>
Establish a robust schema migration foundation using Alembic (async) and refactor models for PostgreSQL compatibility, including a new dedicated Reports table.

Purpose: Versioned schema management is required for production stability; removing create_all ensures consistent state across environments.
Output: Working Alembic setup, initial migration script, and updated models.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phase-2/2-CONTEXT.md
@.planning/phase-2/2-RESEARCH.md
@src/database/models.py
@src/database/session.py
@src/main.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Initialize Alembic with Async Template</name>
  <files>alembic.ini, migrations/env.py, migrations/script.py.mako</files>
  <action>
    1. Initialize Alembic using the async template: `alembic init -t async migrations`.
    2. Update `alembic.ini`:
       - Set `script_location = migrations`.
       - Update `sqlalchemy.url` to the PostgreSQL connection string.
    3. Modify `migrations/env.py`:
       - Import `Base` from `src.database.models`.
       - Set `target_metadata = Base.metadata`.
       - Ensure `DATABASE_URL` is pulled from `src.config.settings.DATABASE_URL`.
  </action>
  <verify>
    Run `alembic current` to ensure Alembic can connect and see the database.
  </verify>
  <done>
    Alembic is initialized with the async template and correctly references the project's metadata.
  </done>
</task>

<task type="auto">
  <name>Task 2: Update Models and Generate Initial Migration</name>
  <files>src/database/models.py, migrations/versions/*.py</files>
  <action>
    1. Update `src/database/models.py`:
       - Add `Report` model with fields for `id`, `thread_id`, `symbol`, `content`, and `created_at`.
       - Ensure all existing models are PostgreSQL-ready.
    2. Generate the initial migration: `alembic revision --autogenerate -m "Initial schema"`.
    3. Verify the generated migration script for accuracy (should include all tables).
  </action>
  <verify>
    Migration script exists in `migrations/versions/` and contains correct `op.create_table` calls.
  </verify>
  <done>
    Schema models are finalized and an initial migration script is prepared.
  </done>
</task>

<task type="auto">
  <name>Task 3: Apply Migrations and Cleanup App Startup</name>
  <files>src/main.py</files>
  <action>
    1. Apply the migration: `alembic upgrade head`.
    2. Modify `src/main.py`:
       - Remove the `Base.metadata.create_all` block from the `lifespan` function.
       - Keep the engine disposal in the shutdown phase.
  </action>
  <verify>
    - `alembic history` shows the migration as applied.
    - Application starts successfully without `create_all` logs.
    - Database tables exist in PostgreSQL.
  </verify>
  <done>
    Database schema is managed solely via Alembic and application startup is cleaned of manual table creation.
  </done>
</task>

</tasks>

<verification>
Check `alembic_version` table in PostgreSQL. Verify `reports` table exists.
</verification>

<success_criteria>
- Alembic is the source of truth for schema changes.
- `src/main.py` is free of `create_all`.
- `Report` model is implemented and persisted.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-2/phase-2-01-SUMMARY.md`
</output>
