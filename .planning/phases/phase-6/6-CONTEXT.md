# Context - Phase 6: Test Coverage

This document captures implementation decisions for Phase 6 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Mocking & Dependency Strategy
- **Layer Coverage:** **Strict Mocking** across all external dependencies.
  - **Database:** Mock at the `AsyncSession` level. Tests should verify that the correct SQL logic/queries are generated (Logic Oriented).
  - **Models:** Mock request and response objects.
  - **External APIs:** Standardize mocks for `yfinance` (Ticker objects) and `DuckDuckGo` (search results).
- **Tooling:** Use standard `unittest.mock` and `pytest-mock` rather than specialized mocking libraries.
- **Data Pattern:** Use **Mocks** (recording and verifying calls) rather than static Fakes for all test data.

## 2. Agent & SSE Verification
- **Graph Mocking:** Mock the entire `.astream_events` method of the compiled LangGraph.
- **Generator Simulation:** Use **Inline Mocks** for async generators. Tests must verify the presence of expected content (Content Focused) rather than a strict sequence of events.
- **Resilience:** Explicitly include tests for **Client Disconnects** and aborted streams during chat interactions.

## 3. Financial Edge Case Priority
- **Calculations:** Test for **Division by Zero** in Average Cost Basis (ACB) and PNL logic (e.g., when quantity reaches 0).
- **Currency/FX:** Verify error handling by ensuring mocked FX service failures **Raise Exceptions**.
- **Consistency:** Test **Strict Consistency** for out-of-order transaction dates (e.g., a SELL before a BUY).
- **Validation:** Focus on **Basic Pydantic Validation** for polymorphic schemas (Real Estate, Funds, etc.).

## 4. Async Test Infrastructure
- **Isolation:** Use **Function Scope** for all async mocks and fixtures to ensure absolute isolation between tests.
- **Standardization:**
  - Use **Explicit Markers** (`@pytest.mark.asyncio`) for all async test functions.
  - Use `httpx.AsyncClient` exclusively for all FastAPI endpoint and integration testing.
- **Observability:** Enable **Failure Logging** to display the `X-Request-ID` in the console whenever an API-related test fails.
