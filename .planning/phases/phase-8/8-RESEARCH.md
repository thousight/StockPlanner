# Phase 8: Test Coverage Expansion - Research

**Researched:** 2026-03-02
**Domain:** Test Automation, LangGraph Verification, Financial Path Coverage
**Confidence:** HIGH

## Summary

This research focuses on expanding test coverage to 80%+ by addressing complex agentic workflows, concurrent database operations, and high-precision financial logic. We identified specific patterns for "teleporting" LangGraph state to test edge-case transitions, simulating concurrency conflicts without deadlocks, and using property-based testing to guarantee correctness in multi-currency ACB calculations.

**Primary recommendation:** Use `graph.update_state(as_node=...)` for targeted agent testing and `hypothesis` for financial invariants.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Core Priority:** Equal focus on **Agent Reasoning Nodes** and the **Service Layer** (Math/FX logic).
- **100% Path Coverage:** The **Financial Math** (Multi-currency Average Cost Basis) in `src/services/portfolio.py` must achieve 100% path coverage.
- **Infrastructure:** Include tests for the **FastAPI Lifespan** and background task scheduler startup in `main.py`.
- **Utilities:** Prioritize unit tests for shared functions in the `utils/` directory (prompt formatting, news parsing).

### Claude's Discretion
- **Internal Agent Verification:** Research/Supervisor/Analyst node-level verification strategy.
- **Lifecycle & Task Simulation:** Method for triggering cleanup logic and verifying TTL.
- **Edge Case & Stress Testing:** Data gaps, timeouts, input stress, and concurrency handling.

### Deferred Ideas (OUT OF SCOPE)
- UI/Frontend testing (Flutter is not part of this milestone).
- Performance benchmarking beyond basic concurrency verification.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pytest` | ^8.0 | Test runner | Industry standard for Python. |
| `pytest-asyncio` | ^0.23 | Async test support | Required for FastAPI and LangGraph. |
| `pytest-cov` | ^4.1 | Coverage reporting | Essential for the 80% and 100% targets. |
| `hypothesis` | ^6.98 | Property-based testing | Best for finding edge cases in financial math. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest-mock` | ^3.12 | Mocking/Spying | For patching LLM calls and external APIs. |
| `freezegun` | ^1.4 | Time mocking | For testing TTL and cleanup logic. |
| `time-machine` | ^2.13 | Faster time mocking | Alternative to freezegun, better for `asyncio`. |
| `httpx` | ^0.27 | Async HTTP client | For testing FastAPI endpoints via `AsyncClient`. |

## Architecture Patterns

### Recommended Test Structure
```
tests/
├── unit/
│   ├── agents/          # Node-level tests (direct function calls)
│   ├── services/        # Portfolio math, FX, logic
│   └── utils/           # Shared helpers
├── integration/
│   ├── test_graph.py    # Subgraph and transition tests
│   ├── test_lifecycle.py# Lifespan and APScheduler cleanup
│   └── test_api.py      # FastAPI endpoints and concurrency
└── conftest.py          # Shared fixtures (DB, Checkpointer)
```

### Pattern 1: LangGraph "Teleportation"
**What:** Using `update_state` with `as_node` to test specific transitions without running the full graph.
**When to use:** Testing conditional edges (e.g., routing from Supervisor to Analyst) or testing a node's output processing.
**Example:**
```python
from langgraph.checkpoint.memory import MemorySaver

# Setup graph with memory checkpointer
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "test"}}

# "Teleport" to a specific node state
app.update_state(config, {"messages": [HumanMessage(content="Analyze AAPL")]}, as_node="supervisor")

# Run next step and verify routing
result = await app.ainvoke(None, config)
assert app.get_state(config).next == ("research_agent",)
```

### Pattern 2: Concurrent Conflict Simulation
**What:** Using `asyncio.gather` with a delayed mock to trigger race conditions.
**When to use:** Verifying `409 Conflict` handling in API endpoints or persistence layers.
**Example:**
```python
async def test_concurrent_updates_conflict(client):
    # Mock a service to be slow
    with patch("src.services.portfolio.update", side_effect=lambda x: asyncio.sleep(0.5)):
        # Fire two requests simultaneously
        resp1, resp2 = await asyncio.gather(
            client.post("/investment/transactions", json=data),
            client.post("/investment/transactions", json=data),
            return_exceptions=True
        )
    # One should succeed, one should return 409
    statuses = [r.status_code for r in [resp1, resp2] if not isinstance(r, Exception)]
    assert 409 in statuses
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Time mocking | `datetime.now()` mocks | `freezegun` / `time-machine` | Handles system-wide clock, including nested calls. |
| Data generation | Manual loop-based testing | `hypothesis` | Finds edge cases (NaN, MaxInt, Empty) you won't think of. |
| Path coverage | Manual branch tracking | `pytest-cov --cov-branch` | Reliable reporting of unvisited code paths. |

## Common Pitfalls

### Pitfall 1: `AsyncMock` vs `Mock` for `to_thread`
**What goes wrong:** Mocking `asyncio.to_thread` with a standard `Mock` causes `TypeError: object X can't be used in 'await' expression`.
**How to avoid:** Always use `AsyncMock` when patching coroutines or `to_thread` wrappers. Prefer patching the *target* function (e.g., `yfinance.download`) which runs in the thread, rather than the thread wrapper itself.

### Pitfall 2: `BackgroundScheduler` in Pytest
**What goes wrong:** The scheduler runs in a separate thread and may not see the `freezegun` mocked time, or the test finishes before the scheduler "ticks".
**How to avoid:** For unit tests, **manually call** the task functions (e.g., `await cleanup_expired_sessions()`) instead of waiting for the scheduler. Use `freezegun` inside these manual calls.

### Pitfall 3: Checkpointer Lock Deadlocks
**What goes wrong:** `AsyncPostgresSaver` uses internal locks. Running multiple tests sharing the same `thread_id` and checkpointer instance can lead to deadlocks if not handled carefully.
**How to avoid:** Ensure each test uses a unique `thread_id` unless explicitly testing concurrency.

## Code Examples

### 100% Path Coverage for Financial Logic
```python
from hypothesis import given, strategies as st
from decimal import Decimal

@given(
    amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10**10")),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10**6")),
    fx_rate=st.decimals(min_value=Decimal("0.1"), max_value=Decimal("10.0"))
)
def test_acb_calculation_invariants(amount, price, fx_rate):
    result = calculate_acb(amount, price, fx_rate)
    # Invariant: ACB can never be negative for a buy
    assert result >= 0
    # Invariant: Precision must be 2 decimal places
    assert result == result.quantize(Decimal("0.01"))
```

### Mocking Tool Calls in LangGraph
```python
# Use interrupt_after to verify tool selection
app = workflow.compile(checkpointer=MemorySaver(), interrupt_after=["research_node"])
config = {"configurable": {"thread_id": "test"}}

await app.ainvoke({"messages": [HumanMessage(content="Get news for TSLA")]}, config)

# Inspect the "tasks" in the state to see what the agent planned
state = app.get_state(config)
tool_calls = state.tasks[0].values['messages'][-1].tool_calls
assert tool_calls[0]['name'] == 'get_stock_news'
assert tool_calls[0]['args']['symbol'] == 'TSLA'
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Mocking `datetime` manually | `time-machine` | 2023+ | Native `asyncio` compatibility and better performance. |
| Integration-only tests | Node-level unit tests | 2024 (LangGraph) | Faster feedback loops and easier edge-case isolation. |
| Manual CSV test data | `hypothesis` strategies | Standard | Exponentially better coverage of boundary conditions. |

## Sources

### Primary (HIGH confidence)
- LangGraph Docs: Testing & Persistence (MemorySaver/update_state)
- FastAPI Docs: Testing Dependencies and Concurrency
- `hypothesis` Official Docs: Ghostwriter and Decimal strategies

### Secondary (MEDIUM confidence)
- `psycopg` Concurrency Patterns (Optimistic locking behavior)
- `pytest-asyncio` Issue tracker (Known issues with thread executors)

## Metadata
**Confidence breakdown:**
- Standard stack: HIGH - Libraries are mature and standard.
- Architecture: HIGH - LangGraph patterns are well-documented for persistence.
- Pitfalls: MEDIUM - Concurrency/Deadlocks can be environment-specific.

**Research date:** 2026-03-02
**Valid until:** 2026-06-01 (Stable ecosystem)
