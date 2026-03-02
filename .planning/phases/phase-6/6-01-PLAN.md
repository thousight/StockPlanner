---
phase: phase-6
plan: 6-01
type: execute
wave: 1
depends_on: []
files_modified: [tests/conftest.py, tests/api/test_health.py, tests/unit/test_logic.py, tests/unit/test_schemas.py]
autonomous: true
requirements: [REQ-032]

must_haves:
  truths:
    - "Test runner captures and displays X-Request-ID on API test failure"
    - "Calculations for ACB and PNL handle zero quantity without crashing"
    - "Out-of-order transactions (SELL before BUY) are correctly detected or handled by consistency logic"
    - "Polymorphic financial models validate correctly from raw dictionaries"
  artifacts:
    - path: "tests/conftest.py"
      provides: "Global async test fixtures and failure hooks"
    - path: "tests/unit/test_logic.py"
      provides: "Validation for core financial math"
    - path: "tests/unit/test_schemas.py"
      provides: "Validation for Pydantic polymorphic models"
  key_links:
    - from: "pytest"
      to: "X-Request-ID"
      via: "pytest_runtest_makereport hook"
    - from: "tests/unit/test_logic.py"
      to: "src/services/portfolio.py"
      via: "direct unit testing of math functions"
---

<objective>
Setup the global testing infrastructure and verify core financial logic and schemas.

Purpose: Ensure a stable foundation for testing with proper async support, observability, and deterministic logic verification.
Output: Global test fixtures, failure logging hook, and unit tests for pure logic.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-6/6-CONTEXT.md
@.planning/phases/phase-6/6-RESEARCH.md
@src/services/portfolio.py
@src/schemas/portfolio.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Global Test Infrastructure</name>
  <files>tests/conftest.py, tests/api/test_health.py</files>
  <action>
    Create a robust testing foundation:
    1.  Create `tests/conftest.py` with:
        - `pytest-asyncio` configuration (default to function scope).
        - `httpx.AsyncClient` fixture using `ASGIMiddleware` or `app` directly.
        - `mock_session` fixture using `unittest.mock.create_autospec(AsyncSession)` with function scope.
        - Custom `pytest_runtest_makereport` hook to extract and print `X-Request-ID` from response headers on failure.
    2.  Create `tests/api/test_health.py` to verify the `AsyncClient` and health check endpoint.
    3.  Ensure `pytest.ini` is configured for async testing.
  </action>
  <verify>
    Run `pytest tests/api/test_health.py`.
    To test the failure hook, temporarily change the expected status code and verify that it prints information about the request/response.
  </verify>
  <done>Global fixtures and failure logging are operational and verified with a basic health check.</done>
</task>

<task type="auto">
  <name>Task 2: Core Financial Logic Tests</name>
  <files>tests/unit/test_logic.py</files>
  <action>
    Implement unit tests for critical financial calculations in isolation:
    1.  Test Average Cost Basis (ACB) calculation across multiple BUY/SELL events.
    2.  Test PNL calculation for various price movements.
    3.  **Critical:** Test for Division by Zero scenarios in `src/services/portfolio.py` (e.g., when portfolio quantity reaches 0).
    4.  **Critical:** Test for "Strict Consistency" failures when transaction dates are out of order (SELL before a BUY resulting in negative balance at a point in time).
    5.  Use pure unit tests (no DB mocks needed for the core math functions themselves).
  </action>
  <verify>Run `pytest tests/unit/test_logic.py` and ensure all edge cases pass.</verify>
  <done>Financial logic handles edge cases and consistency requirements correctly.</done>
</task>

<task type="auto">
  <name>Task 3: Polymorphic Schema Validation</name>
  <files>tests/unit/test_schemas.py</files>
  <action>
    Verify validation logic for complex financial data structures:
    1.  Test Pydantic models in `src/schemas/portfolio.py` (and `transactions.py`).
    2.  Focus on polymorphic metadata (e.g., ensuring a dictionary with `type: "stock"` validates as `StockMetadata` and `type: "reit"` as `REITMetadata`).
    3.  Test validation for fractional shares and currency codes.
  </action>
  <verify>Run `pytest tests/unit/test_schemas.py`.</verify>
  <done>Polymorphic financial schemas validate raw dictionary inputs correctly across all types.</done>
</task>

</tasks>

<verification>
Check for correct use of @pytest.mark.asyncio.
Verify that no real database connections are attempted.
Confirm that X-Request-ID failure logging works as intended.
</verification>

<success_criteria>
- pytest runner is configured with async support.
- Failure logging hook displays X-Request-ID for failed API tests.
- Financial calculation unit tests cover division by zero and out-of-order dates.
- Polymorphic schemas validate correctly for different asset types.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-6/phase-6-6-01-SUMMARY.md`
</output>
