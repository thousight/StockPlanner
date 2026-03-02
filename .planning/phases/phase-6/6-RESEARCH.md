# Phase 6: Test Coverage - Research

**Researched:** 2026-03-02
**Domain:** Testing (FastAPI, SQLAlchemy 2.0, LangGraph, pytest)
**Confidence:** HIGH

## Summary

This research identifies the technical patterns and pitfalls for implementing a comprehensive test suite for the StockPlanner API. The core challenge is the asynchronous, streaming nature of the agentic workflows and the specific requirements for mocking complex dependencies like SQLAlchemy 2.0's `AsyncSession` and LangGraph's event streams.

**Primary recommendation:** Use a tiered testing approach: Node isolation for logic, Graph stubs for flow, and SSE-aware `httpx.AsyncClient` for endpoint integration.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Layer Coverage:** **Strict Mocking** across all external dependencies.
  - **Database:** Mock at the `AsyncSession` level. Verify SQL logic/queries (Logic Oriented).
  - **Models:** Mock request and response objects.
  - **External APIs:** Standardize mocks for `yfinance` (Ticker objects) and `DuckDuckGo` (search results).
- **Tooling:** Use standard `unittest.mock` and `pytest-mock`.
- **Data Pattern:** Use **Mocks** (recording calls) rather than static Fakes.
- **Graph Mocking:** Mock the entire `.astream_events` method of the compiled LangGraph.
- **Generator Simulation:** Use **Inline Mocks** for async generators. Verify Content Focused.
- **Resilience:** Tests for **Client Disconnects** and aborted streams.
- **Calculations:** Test for **Division by Zero** in ACB and PNL logic.
- **Consistency:** Test **Strict Consistency** for out-of-order transaction dates (SELL before BUY).
- **Validation:** Focus on **Basic Pydantic Validation** for polymorphic schemas.
- **Isolation:** Use **Function Scope** for all async mocks and fixtures.
- **Standardization:**
  - Use **Explicit Markers** (`@pytest.mark.asyncio`).
  - Use `httpx.AsyncClient` exclusively for API tests.
- **Observability:** Enable **Failure Logging** to display `X-Request-ID` on failure.

### Claude's Discretion
- Implementation of the global `X-Request-ID` failure logger in pytest.
- Specific async generator simulation logic for token streaming.
- Strategy for verifying state transitions in mid-graph execution.

### Deferred Ideas (OUT OF SCOPE)
- UI/Frontend testing (Flutter).
- Load testing or performance benchmarking.
- Real LLM integration testing (cost/flakiness avoidance).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-032 | Update pytest to cover FastAPI endpoints and integration with cloud database. | Validated `httpx.AsyncClient` patterns and `AsyncSession` mocking. |
| SSE-TEST | Verify token-level streaming and client disconnects. | Documented `astream_events` mocking and `request.is_disconnected()` pitfalls. |
| LOGIC-TEST | Verify financial calculations (ACB, PNL) and consistency. | Specified node-isolation testing for pure logic functions. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pytest` | ^8.0.0 | Test runner | Industry standard for Python. |
| `pytest-asyncio` | ^0.23.0 | Async test support | Required for FastAPI/SQLAlchemy async tests. |
| `pytest-mock` | ^3.12.0 | Mocking wrapper | Provides the `mocker` fixture, cleaner than `unittest.mock.patch`. |
| `httpx` | ^0.27.0 | HTTP Client | Official client recommended by FastAPI for testing. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|--------------|
| `sqlalchemy[asyncio]` | 2.0.x | Type hints for mocking | Use `create_autospec(AsyncSession)` for safe mocks. |
| `pandas` | ^2.0.0 | Data structures | Needed for mocking `yfinance` historical data returns. |

## Architecture Patterns

### Recommended Project Structure
```
tests/
├── conftest.py          # Global fixtures (client, mock_db, failure_logger)
├── unit/
│   ├── test_logic.py    # Financial calculations (ACB, PNL)
│   └── test_nodes.py    # LangGraph nodes in isolation
├── integration/
│   ├── test_graph.py    # LangGraph routing and state transitions
│   └── test_tools.py    # Mocks for yfinance/DDG
└── api/
    ├── test_chat.py     # SSE Streaming and Disconnects
    └── test_portfolio.py # CRUD and Analytics endpoints
```

### Pattern 1: Mocking AsyncSession Result Chain
**What:** Mocking the fluent API of SQLAlchemy 2.0 `AsyncSession`.
**When to use:** Any test interacting with the database layer.
**Example:**
```python
# Source: Verified SQLAlchemy 2.0 patterns
from unittest.mock import AsyncMock, MagicMock

mock_session = AsyncMock()
mock_result = MagicMock()
# Mocking: result = await session.execute(...); items = result.scalars().all()
mock_session.execute.return_value = mock_result
mock_result.scalars.return_value.all.return_value = [item1, item2]
```

### Pattern 2: LangGraph Node Isolation
**What:** Testing agent nodes as pure functions by passing state dictionaries.
**When to use:** Testing logic within specific agent steps (e.g., analyst calculations).
**Why:** Bypasses graph overhead and LLM costs; highly deterministic.

### Pattern 3: X-Request-ID Failure Hook
**What:** Capturing the `X-Request-ID` header from a failed FastAPI request and printing it.
**How:**
1. Custom `httpx.AsyncClient` fixture attaches the last response to `request.node`.
2. `pytest_runtest_makereport` hook reads from `item` and logs the ID on failure.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Stream Consumption | Custom while loops | `response.aiter_lines()` | Handles chunking and buffering correctly. |
| Mocking yfinance | Custom Ticker class | `mocker.patch("yfinance.Ticker")` | Easier to control the instance returned by the constructor. |
| Async Event Loop | Manual loop mgmt | `@pytest.mark.asyncio` | Manages loop lifecycle and context cleanup automatically. |

## Common Pitfalls

### Pitfall 1: Hanging Streaming Tests
**What goes wrong:** Test hangs indefinitely when calling a streaming endpoint.
**Why it happens:** The `AsyncClient` and FastAPI app share an event loop. If the stream isn't consumed (iterated), the generator remains suspended.
**How to avoid:** Always use `async with client.stream(...)` and iterate using `aiter_lines()` or `aiter_bytes()`.

### Pitfall 2: Disconnect Detection Failure
**What goes wrong:** Server logic for "client disconnected" never triggers in tests.
**Why it happens:** Exiting the client context manager doesn't always send the `http.disconnect` signal immediately in a mock transport.
**How to avoid:** Ensure the server-side generator uses `try/finally` blocks and check `await request.is_disconnected()` frequently.

### Pitfall 3: Session Mock Leakage
**What goes wrong:** Database mocks from one test interfere with another.
**How to avoid:** Use `function` scope for all database-related fixtures (as specified in CONTEXT.md).

## Code Examples

### Simulating LangGraph SSE Events
```python
# Source: Verified LangGraph testing pattern
async def mock_stream(*args, **kwargs):
    events = [
        {"event": "on_chat_model_stream", "data": {"chunk": "Hello"}},
        {"event": "on_chat_model_stream", "data": {"chunk": " World"}},
        {"event": "on_chain_end", "data": {"output": "Hello World"}}
    ]
    for event in events:
        yield event

mock_graph.astream_events.side_effect = mock_stream
```

### Mocking yfinance Ticker
```python
import pandas as pd
mock_ticker = mocker.Mock()
mock_ticker.history.return_value = pd.DataFrame({"Close": [100.0]}, index=[pd.Timestamp.now()])
mocker.patch("yfinance.Ticker", return_value=mock_ticker)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `unittest.mock.patch` | `mocker` fixture | Pytest 3.x | Safer cleanup, less boilerplate. |
| `client.get()` (sync) | `httpx.AsyncClient` | FastAPI/Starlette | Native async support, better SSE handling. |
| Mocking Graph Output | `astream_events` | LangGraph v0.1+ | Allows testing of granular intermediate steps. |

## Open Questions

1. **Wait time for Disconnects:** 
   - What we know: `httpx` transport signals disconnect on exit.
   - What's unclear: The exact timing/delay before `request.is_disconnected()` returns `True`.
   - Recommendation: Use a small `asyncio.sleep` in the server generator during tests to allow signal propagation.

2. **Polymorphic Schema Validation:**
   - What we know: Pydantic handles `Union` types for polymorphism.
   - What's unclear: Complexity of mocks for deep nested financial structures (e.g., REIT vs Stock).
   - Recommendation: Use `model_validate` with raw dicts in tests to verify discriminator logic.

## Sources

### Primary (HIGH confidence)
- [FastAPI Docs] - Testing StreamingResponse with `httpx`.
- [SQLAlchemy 2.0 Docs] - `AsyncSession` API and result methods.
- [LangGraph Docs] - Unit testing nodes and using `astream_events`.

### Secondary (MEDIUM confidence)
- [Pytest Documentation] - `pytest_runtest_makereport` hook patterns.
- [Community Blog Posts] - Common patterns for mocking `yfinance`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries are mature and well-documented.
- Architecture: HIGH - Tiered testing is the standard for LLM/Agentic apps.
- Pitfalls: HIGH - Documented issues in FastAPI/Httpx ecosystem.

**Research date:** 2026-03-02
**Valid until:** 2026-06-02
