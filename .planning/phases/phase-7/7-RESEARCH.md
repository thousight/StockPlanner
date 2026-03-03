# Phase 7: Simplification & Cleanup - Research

**Researched:** 2025-03-02
**Domain:** Code Audit & Refactoring
**Confidence:** HIGH

## Summary
The audit of the StockPlanner codebase reveals significant technical debt from the rapid transition to an async API architecture. The primary issues are redundant `yfinance` call sites, blocking synchronous IO within async functions, and legacy test paths that cause CI failures.

## User Constraints
### Locked Decisions
- Agent nodes are strictly prohibited from implementing data manipulation logic.
- Market data unified in `src/services/market_data.py`.
- No shared "Base Agent" class (remove `src/graph/agents/base.py`).
- Financial math resides strictly in `src/services/portfolio.py`.
- Unused imports/functions removed immediately.
- Standardized logging prefix: `[AGENT_NAME]` including `thread_id` and `request_id`.

## Standard Stack
- **yfinance**: Must be wrapped in `asyncio.to_thread` for all calls to prevent event loop blocking.
- **FastAPI**: Standardization on `HTTPException` for interface errors.
- **pytest**: Fix broken legacy test paths.

## Architecture Patterns
- **Service-First Data**: Agent Nodes -> Agent Tools -> Business Services. Nodes must never call database or external APIs directly.
- **Consolidated Market Data**: All `yfinance` logic (FX rates, current prices, news urls) must be centralized in `src/services/market_data.py`.
- **Async Safety**: Use `asyncio.to_thread` for all `yfinance` methods (`Ticker.info`, `Ticker.news`, `Ticker.history`).

## Don't Hand-Roll
- **Financial Calculations**: Do not implement ACB or PNL logic in agents or tools; call `src/services/portfolio.py`.
- **Pricing Logic**: Do not implement price fallback logic in agents; call `src/services/market_data.py`.

## Common Pitfalls
- **Sync Blocking**: `yf.Ticker(symbol).fast_info` is a blocking call. If used in an `async` route, it blocks all other requests.
- **Path Drift**: Many tests in the root `tests/` directory are using `src.agents` or `src.tools`, which now live under `src.graph`.
- **Circular Imports**: Moving news logic from `src/graph/utils/news.py` to `src/services/market_data.py` may cause cycles if the service also imports graph components.

## Code Examples

### Standardized Async Wrapper for yfinance
```python
import asyncio
import yfinance as yf

async def get_current_price_async(symbol: str):
    ticker = yf.Ticker(symbol)
    # yfinance is blocking, wrap in thread pool
    info = await asyncio.to_thread(lambda: ticker.fast_info)
    return info.get("last_price")
```

### Standardized Agent Logging
```python
import logging
logger = logging.getLogger(__name__)

# Inside agent node
logger.info(f"[{AGENT_NAME.upper()}] [Thread: {thread_id}] [Request: {request_id}] Executing step...")
```

## Legacy Artifacts for Removal
- `src/graph/agents/base.py` (Unused base class)
- `tests/test_analyst_agent.py` (Legacy path)
- `tests/test_crud.py` (Legacy path)
- `tests/test_research_tools.py` (Legacy path)
- `tests/test_supervisor_agent.py` (Legacy path)
