# Plan Summary - Phase 7-01: Unified Market Data Service & Async Safety

## Implementation Summary
Successfully centralized all external market data dependencies into a single, async-safe service layer. This cleanup reduces redundant code across tools and services while ensuring the FastAPI event loop is never blocked by synchronous `yfinance` calls.

- **Centralized yfinance Logic:** Moved all direct `yfinance` imports and logic from tools (`news.py`, `research.py`), services (`portfolio.py`, `benchmarking.py`), and utils (`news.py`) into `src/services/market_data.py`.
- **Async Thread Wrapping:** Wrapped every `yfinance` method call (including `.info`, `.news`, `.history`, and `.fast_info`) in `asyncio.to_thread`. This prevents blocking the main thread during network IO with synchronous SDKs.
- **Unified Service Interface:** Created standardized async functions in `src/services/market_data.py`:
  - `get_current_price_async`: Standardized price fetching with fallback logic.
  - `get_historical_prices_async`: Simplified history retrieval for PNL and benchmarking.
  - `get_stock_news_data`: Unified news URL fetching and parsing.
  - `get_stock_financials_data`: Centralized financial statement retrieval.
- **Dependency Refactoring:** Updated all dependent modules to use the new `market_data` service, significantly simplifying their import blocks and internal logic.

## File Changes
- `src/services/market_data.py`: Now the sole owner of `yfinance` dependencies and async-wrapped data fetching.
- `src/services/portfolio.py`: Refactored to remove direct `yfinance` usage; uses `get_historical_prices_async`.
- `src/services/benchmarking.py`: Refactored to remove direct `yfinance` usage; uses `get_historical_prices_async`.
- `src/graph/tools/news.py`: Refactored to use unified news services.
- `src/graph/tools/research.py`: Refactored to use centralized financial data retrieval.
- `src/graph/utils/news.py`: Cleaned up to delegate news fetching to the service layer.

## Technical Decisions
- **Threading Pattern:** Used `asyncio.to_thread` for all `yfinance` interactions as it is the most robust pattern for wrapping synchronous IO in an asynchronous FastAPI environment.
- **Service-First Architecture:** Enforced a "tools only call services" pattern, ensuring that agentic tools remain thin wrappers over core business logic.

## Verification
- Code review confirms no direct `yfinance` imports remain outside of `src/services/market_data.py`.
- Verified all `yfinance` call sites use `await asyncio.to_thread`.
- API tests for portfolio and news tools confirm the refactored services return data correctly.
