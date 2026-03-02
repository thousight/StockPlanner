---
phase: phase-6
plan: 6-02
type: execute
wave: 2
depends_on: [6-01]
files_modified: [tests/unit/test_crud.py, tests/integration/test_tools.py]
autonomous: true
requirements: [REQ-032]

must_haves:
  truths:
    - "Database operations are verified using strict AsyncSession mocks without a live DB"
    - "External tools (yfinance, DuckDuckGo) return deterministic mock data in tests"
  artifacts:
    - path: "tests/unit/test_crud.py"
      provides: "Verification of DB interaction logic"
    - path: "tests/integration/test_tools.py"
      provides: "Strictly mocked integration tests for external APIs"
  key_links:
    - from: "tests/unit/test_crud.py"
      to: "SQLAlchemy AsyncSession"
      via: "AsyncMock and spec-based mocking"
    - from: "tests/integration/test_tools.py"
      to: "yfinance.Ticker"
      via: "mocker.patch"
---

<objective>
Implement strict mocking patterns for the database layer and external financial tools.

Purpose: Ensure that all database and third-party API interactions are deterministic, fast, and independent of external state.
Output: Verified mocking patterns for SQLAlchemy and external SDKs.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-6/6-01-PLAN.md
@.planning/phases/phase-6/6-CONTEXT.md
@.planning/phases/phase-6/6-RESEARCH.md
@src/database/models.py
@src/graph/tools/research.py
@src/graph/tools/news.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: AsyncSession Mocking & CRUD Verification</name>
  <files>tests/unit/test_crud.py</files>
  <action>
    Implement strict database mocking patterns:
    1.  Refactor or create `tests/unit/test_crud.py`.
    2.  Use the `mock_session` fixture from `conftest.py`.
    3.  Mock the fluent API of SQLAlchemy 2.0: `session.execute()`, `result.scalars()`, `result.one_or_none()`, etc.
    4.  Verify that CRUD functions (create, read, update, delete) call the expected session methods with correct arguments.
    5.  Ensure NO real database connection is initiated (verify by checking for `SQLALCHEMY_DATABASE_URL` usage or network calls).
  </action>
  <verify>Run `pytest tests/unit/test_crud.py` and ensure it passes without a database running.</verify>
  <done>Database operations are verified via session-level mocking with logic-oriented assertions.</done>
</task>

<task type="auto">
  <name>Task 2: External Tool Mocks (yfinance, DuckDuckGo)</name>
  <files>tests/integration/test_tools.py</files>
  <action>
    Implement strictly mocked integration tests for agent tools:
    1.  Create `tests/integration/test_tools.py`.
    2.  Mock `yfinance.Ticker` to return a mock object that provides deterministic `.history()` (pandas DataFrame) and `.info` (dict).
    3.  Mock `DuckDuckGoSearchAPIWrapper` or the specific search function used in `src/graph/tools/`.
    4.  Verify that tools correctly parse and return data matching the expected internal schemas.
    5.  Verify that tool failure modes (e.g., empty search results, API errors) are handled gracefully.
  </action>
  <verify>Run `pytest tests/integration/test_tools.py` and ensure no external network requests are made.</verify>
  <done>External API dependencies are fully isolated using deterministic mocks.</done>
</task>

</tasks>

<verification>
Confirm that `AsyncMock` is used for all async database calls.
Check that `mocker.patch` correctly targets the import location of external libraries.
</verification>

<success_criteria>
- CRUD tests pass using AsyncSession mocks exclusively.
- Tool integration tests pass using deterministic mock data.
- Zero network/database dependencies in the test suite for these components.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-6/phase-6-6-02-SUMMARY.md`
</output>
