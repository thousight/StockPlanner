---
phase: phase-7
plan: 7-01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/services/market_data.py
  - src/services/portfolio.py
  - src/services/benchmarking.py
  - src/graph/tools/news.py
  - src/graph/tools/research.py
  - src/graph/utils/news.py
autonomous: true
requirements: [Audit]
---

<objective>
Unify all yfinance logic into `src/services/market_data.py` and ensure async safety using `asyncio.to_thread`. 

Purpose: Prevent blocking the event loop and centralize external data fetching for better maintainability.
Output: A robust, async-safe market data service used by all tools and services.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/phase-7/7-CONTEXT.md
@.planning/phases/phase-7/7-RESEARCH.md
@src/services/market_data.py
@src/services/portfolio.py
@src/services/benchmarking.py
@src/graph/utils/news.py
@src/graph/tools/news.py
@src/graph/tools/research.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Centralize and Async-wrap yfinance in Market Data Service</name>
  <files>src/services/market_data.py</files>
  <action>
    - Move `fetch_yfinance_news_urls` and `_parse_yf_news_item` from `src/graph/utils/news.py` to `src/services/market_data.py`.
    - Implement `get_ticker_async(symbol: str)` helper that returns a yf.Ticker object.
    - Implement the following async functions in `src/services/market_data.py`, wrapping all `yfinance` calls in `asyncio.to_thread`:
      - `get_historical_fx_rate`: Wrap `ticker.history`.
      - `validate_transaction_price`: Wrap `ticker.history`.
      - `get_current_price`: Wrap `ticker.fast_info`.
      - `get_stock_financials_data`: (New) Fetches `ticker.info` for the Research tool.
      - `get_stock_news_data`: (New) Fetches `ticker.news` for the News tool.
      - `get_historical_prices_async`: (New) Fetches `ticker.history` for benchmarking.
    - Move news caching logic (`get_valid_cache`, `save_cache`) from `src/services/portfolio.py` to `src/services/market_data.py`.
  </action>
  <verify>
    Check `src/services/market_data.py` for `asyncio.to_thread` usage in all `yfinance` methods.
    Verify all moved functions are present and exported.
  </verify>
  <done>
    `src/services/market_data.py` is the single source of truth for yfinance and is async-safe.
  </done>
</task>

<task type="auto">
  <name>Task 2: Refactor Tools to use Market Data Service</name>
  <files>
    - src/graph/tools/news.py
    - src/graph/tools/research.py
    - src/graph/utils/news.py
  </files>
  <action>
    - In `src/graph/tools/news.py`:
      - Remove `import yfinance as yf`.
      - Update `get_stock_news` and `get_macro_economic_news` to call `get_stock_news_data` from `src/services/market_data.py`.
    - In `src/graph/tools/research.py`:
      - Remove `import yfinance as yf`.
      - Update `get_stock_financials` to use `get_stock_financials_data` from `src/services/market_data.py`.
    - In `src/graph/utils/news.py`:
      - Remove logic migrated to `market_data.py`.
      - Keep only non-yfinance utilities (like article scraping/summarization) or mark for deletion in next plan.
  </action>
  <verify>
    `grep "import yfinance" src/graph/tools/` returns no matches.
    `pytest tests/integration/test_tools.py` (if it exists and is not legacy).
  </verify>
  <done>
    Agent tools no longer depend directly on yfinance.
  </done>
</task>

<task type="auto">
  <name>Task 3: Refactor Services to use Market Data Service</name>
  <files>
    - src/services/portfolio.py
    - src/services/benchmarking.py
  </files>
  <action>
    - In `src/services/portfolio.py`:
      - Remove `import yfinance as yf`.
      - Remove `get_valid_cache` and `save_cache` (migrated to market_data).
      - Update `get_portfolio_summary` to use `get_historical_prices_async` from `market_data.py` for yesterday's price.
    - In `src/services/benchmarking.py`:
      - Remove `import yfinance as yf`.
      - Update `get_spy_performance` to use `get_historical_prices_async` from `market_data.py`.
  </action>
  <verify>
    `grep "import yfinance" src/services/` only returns matches in `market_data.py`.
  </verify>
  <done>
    Business services no longer depend directly on yfinance.
  </done>
</task>

</tasks>

<verification>
- All `yfinance` calls in `src/` are centralized in `src/services/market_data.py`.
- Every `yfinance` call (Ticker.info, Ticker.news, Ticker.history, Ticker.fast_info) is wrapped in `asyncio.to_thread`.
- News caching is moved to a more appropriate service.
</verification>

<success_criteria>
- No `import yfinance` in any file except `src/services/market_data.py`.
- No blocking yfinance calls in async functions.
- Tools and services correctly retrieve data via the market data service.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-7/phase-7-01-SUMMARY.md`
</output>
