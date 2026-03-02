---
phase: phase-2
plan: 2-02
type: execute
wave: 2
depends_on: [2-01]
files_modified: [src/main.py, src/graph/persistence.py, src/lifecycle/tasks.py]
autonomous: true
requirements: [REQ-012]
user_setup: []
must_haves:
  truths:
    - "LangGraph state is persisted to PostgreSQL"
    - "Conversation states are cleaned up after 30 days"
    - "News cache entries are cleaned up after 24 hours"
  artifacts:
    - path: "src/graph/persistence.py"
      provides: "AsyncPostgresSaver configuration"
    - path: "src/lifecycle/tasks.py"
      provides: "TTL cleanup logic"
  key_links:
    - from: "src/main.py"
      to: "src/lifecycle/tasks.py"
      via: "APScheduler startup"
      pattern: "scheduler\.add_job"
---

<objective>
Implement LangGraph state persistence using AsyncPostgresSaver and setup automated data lifecycle management via APScheduler for TTL cleanups.

Purpose: Persistence allows multi-turn conversations and recovery; TTLs prevent database bloat.
Output: Configured checkpointer and background cleanup service.
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
@src/main.py
@src/database/session.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Setup AsyncPostgresSaver</name>
  <files>src/graph/persistence.py</files>
  <action>
    1. Create `src/graph/persistence.py`.
    2. Implement `get_checkpointer()` using `AsyncPostgresSaver.from_conn_string(settings.DATABASE_URL)`.
    3. Configure it with `JsonPlusSerializer(pickle_fallback=True)` to handle nested agent state.
    4. Ensure it uses the same database pool or connection parameters as the rest of the app.
  </action>
  <verify>
    Verify `get_checkpointer()` returns an instance of `AsyncPostgresSaver`.
  </verify>
  <done>
    LangGraph checkpointer is ready for use in the agent graph.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement TTL Cleanup Tasks</name>
  <files>src/lifecycle/tasks.py</files>
  <action>
    1. Create `src/lifecycle/tasks.py`.
    2. Implement `cleanup_checkpoints()`:
       - SQL to delete rows from `checkpoints` older than 30 days.
       - Cascade cleanup for `checkpoint_blobs` and `checkpoint_writes` (avoiding orphans).
    3. Implement `cleanup_news_cache()`:
       - SQL to delete rows from `news_cache` where `expire_at < NOW()`.
  </action>
  <verify>
    Test the SQL queries manually or via a script to ensure they correctly target expired rows.
  </verify>
  <done>
    Cleanup logic for state and cache is implemented using set-based SQL deletes.
  </done>
</task>

<task type="auto">
  <name>Task 3: Integrate APScheduler into FastAPI Lifespan</name>
  <files>src/main.py</files>
  <action>
    1. Update `src/main.py` lifespan:
       - Initialize `AsyncIOScheduler`.
       - Schedule `cleanup_checkpoints` to run daily (e.g., at 02:00 AM).
       - Schedule `cleanup_news_cache` to run hourly or daily.
       - Start the scheduler on startup and shut it down on shutdown.
  </action>
  <verify>
    Check application logs on startup to confirm scheduler has started without errors.
  </verify>
  <done>
    Automated data lifecycle management is active in the production application.
  </done>
</task>

</tasks>

<verification>
Verify `AsyncPostgresSaver` tables (`checkpoints`, etc.) are created in the database.
</verification>

<success_criteria>
- LangGraph state persists across application restarts.
- Background tasks are scheduled and running.
- TTL logic correctly targets old data.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-2/phase-2-02-SUMMARY.md`
</output>
