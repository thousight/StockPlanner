---
phase: phase-6
plan: 6-03
type: execute
wave: 3
depends_on: [6-02]
files_modified: [tests/api/test_portfolio.py, tests/api/test_transactions.py, tests/api/test_threads.py]
autonomous: true
requirements: [REQ-032]

must_haves:
  truths:
    - "Portfolio and Transaction CRUD endpoints return 200/201 with correct JSON schemas"
    - "Thread management endpoints correctly interact with mocked persistence layers"
  artifacts:
    - path: "tests/api/test_portfolio.py"
      provides: "Verification of portfolio analytics API"
    - path: "tests/api/test_transactions.py"
      provides: "Verification of transaction CRUD API"
    - path: "tests/api/test_threads.py"
      provides: "Verification of thread lifecycle API"
  key_links:
    - from: "tests/api/test_portfolio.py"
      to: "src/controllers/portfolio.py"
      via: "httpx.AsyncClient.get"
    - from: "tests/api/test_transactions.py"
      to: "src/controllers/transactions.py"
      via: "httpx.AsyncClient.post"
---

<objective>
Verify the functionality of RESTful API endpoints for financial data and thread management.

Purpose: Ensure that the API layer correctly orchestrates services and database interactions.
Output: Comprehensive test suite for CRUD and analytics endpoints.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-6/6-02-PLAN.md
@.planning/phases/phase-6/6-CONTEXT.md
@.planning/phases/phase-6/6-RESEARCH.md
@src/controllers/portfolio.py
@src/controllers/transactions.py
@src/controllers/threads.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Portfolio & Transaction API Tests</name>
  <files>tests/api/test_portfolio.py, tests/api/test_transactions.py</files>
  <action>
    Implement integration tests for financial CRUD endpoints:
    1.  Test `GET /investment` (Portfolio Analytics): Mock the service layer to return deterministic metrics. Verify JSON structure and numeric precision.
    2.  Test `POST /investment/transactions`: Verify creation of transactions with polymorphic metadata.
    3.  Test `GET`, `PUT`, `DELETE` for individual transactions.
    4.  Verify error responses for invalid inputs (Pydantic validation) and non-existent records (404).
    5.  Use the `httpx.AsyncClient` from `conftest.py`.
  </action>
  <verify>Run `pytest tests/api/test_portfolio.py tests/api/test_transactions.py`.</verify>
  <done>Core financial endpoints are verified for both happy-path and error scenarios.</done>
</task>

<task type="auto">
  <name>Task 2: Thread & Lifecycle API Tests</name>
  <files>tests/api/test_threads.py</files>
  <action>
    Implement integration tests for thread management:
    1.  Test `GET /threads`: Verify retrieval of active conversation threads.
    2.  Test `DELETE /threads/{id}`: Verify thread deletion logic.
    3.  Mock the database session used by the thread controllers.
    4.  Verify that correct headers (e.g., `X-Request-ID`) are present in responses.
  </action>
  <verify>Run `pytest tests/api/test_threads.py`.</verify>
  <done>Thread management and lifecycle endpoints are verified using mocked persistence.</done>
</task>

</tasks>

<verification>
Ensure all tests use `httpx.AsyncClient`.
Check that service-level mocks are isolated and do not persist across tests.
</verification>

<success_criteria>
- Portfolio analytics endpoint returns correct aggregated data (mocked).
- Transaction CRUD operations (POST, GET, PUT, DELETE) pass with schema validation.
- Thread management endpoints correctly handle requests via mocked session.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-6/phase-6-6-03-SUMMARY.md`
</output>
