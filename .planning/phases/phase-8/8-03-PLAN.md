---
phase: phase-8
plan: 8-03
type: execute
wave: 3
depends_on: [8-02]
files_modified:
  - tests/unit/test_lifecycle.py
  - tests/api/test_concurrency.py
  - tests/api/test_stress.py
autonomous: true
requirements:
  - REQ-032
must_haves:
  truths:
    - "FastAPI lifespan correctly initializes and disposes of database and checkpointer resources."
    - "Background cleanup tasks correctly delete expired checkpoints and news cache entries using mocked time."
    - "Concurrent requests for the same thread_id are rejected with a 409 Conflict."
    - "The API remains stable under input stress and handles LLM timeouts without crashing."
  artifacts:
    - path: "tests/unit/test_lifecycle.py"
      provides: "Verification of lifespan hooks and scheduled task execution with time-machine"
    - path: "tests/api/test_concurrency.py"
      provides: "Stress tests for 409 Conflict handling on shared thread_id"
    - path: "tests/api/test_stress.py"
      provides: "Verification of system resilience against long inputs and network timeouts"
  key_links:
    - from: "main.py"
      to: "tests/api/test_concurrency.py"
      via: "thread_concurrency_protection middleware verification"
    - from: "src/lifecycle/tasks.py"
      to: "tests/unit/test_lifecycle.py"
      via: "direct task invocation with mocked database and time"
---

<objective>
Verify the FastAPI lifespan and background scheduler logic using time-mocking, and implement stress tests for concurrency conflicts and resilience against network timeouts and malformed inputs.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-8/8-CONTEXT.md
@.planning/phases/phase-8/8-RESEARCH.md
@main.py
@src/lifecycle/tasks.py
@src/graph/persistence.py
@src/graph/graph.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Lifecycle & Scheduler Verification</name>
  <files>tests/unit/test_lifecycle.py</files>
  <action>
    Implement unit tests for the background scheduler and lifespan functionality.
    
    Implementation details:
    - Lifespan: Mock `get_checkpointer` and `engine` to verify they are correctly initialized (setup called) and disposed of during the FastAPI startup/shutdown cycle.
    - Scheduler Tasks: Use `time-machine` to mock the system clock. Manually call `cleanup_checkpoints` and `cleanup_news_cache` with various mocked times.
    - Database Mocking: Mock `psycopg.AsyncConnection` and verify that the SQL `DELETE` queries use the correct logic (e.g., Interval '30 days' for checkpoints, comparing `expire_at` with `NOW()` for news). Verify that background failures are caught and logged without crashing.
  </action>
  <verify>
    Run `pytest tests/unit/test_lifecycle.py`
  </verify>
  <done>
    FastAPI lifespan and background cleanup tasks are verified for correct timing and SQL execution.
  </done>
</task>

<task type="auto">
  <name>Task 2: Concurrency & Stress Verification</name>
  <files>tests/api/test_concurrency.py, tests/api/test_stress.py</files>
  <action>
    Implement API-level stress and concurrency tests.
    
    Implementation details:
    - Concurrency Conflict: Use `asyncio.gather` with `httpx.AsyncClient` to send two identical POST requests to `/chat` (or any graph-related endpoint) with the same `X-Thread-ID` header. Verify that one returns 200 and the other 409 Conflict.
    - Input Stress: Send extremely long (>10,000 chars) or malformed (special characters, empty fields) messages to `/chat`. Verify 4xx errors for schema violations or successful (but safe) processing.
    - Resilience/Timeouts: Mock LLM calls (e.g., `ChatOpenAI.ainvoke`) to simulate network delays exceeding typical timeouts. Verify that the API returns an appropriate 504 error or handles the timeout gracefully without hanging resources.
  </action>
  <verify>
    Run `pytest tests/api/test_concurrency.py tests/api/test_stress.py`
  </verify>
  <done>
    The API is resilient against concurrent requests for the same thread and handles stress/timeouts without crashing.
  </done>
</task>

</tasks>

<verification>
Run all lifecycle and stress tests:
`pytest tests/unit/test_lifecycle.py tests/api/test_concurrency.py tests/api/test_stress.py`
</verification>

<success_criteria>
- Lifespan hooks are verified for proper resource management.
- Background tasks correctly clean up expired data.
- 409 Conflicts are triggered and handled for shared thread IDs.
- No system crashes under input stress or mocked LLM timeouts.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-8/8-03-SUMMARY.md`
</output>
