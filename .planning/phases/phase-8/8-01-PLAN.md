---
phase: phase-8
plan: 8-01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/unit/services/test_portfolio_math.py
  - tests/unit/services/test_market_data.py
  - tests/unit/utils/test_graph_utils.py
autonomous: true
requirements:
  - REQ-032
must_haves:
  truths:
    - "Portfolio math functions are verified for 100% path coverage using property-based testing."
    - "Market data service gracefully handles yfinance failures and empty results."
    - "Graph utility functions (prompt, news, logging) are robust against malformed or missing state data."
  artifacts:
    - path: "tests/unit/services/test_portfolio_math.py"
      provides: "Hypothesis-based verification for ACB and PNL calculations"
    - path: "tests/unit/services/test_market_data.py"
      provides: "Unit tests for external API resilience and caching"
    - path: "tests/unit/utils/test_graph_utils.py"
      provides: "Tests for state-to-prompt conversion and news parsing"
  key_links:
    - from: "tests/unit/services/test_portfolio_math.py"
      to: "src/services/portfolio.py"
      via: "import and direct call"
    - from: "tests/unit/services/test_market_data.py"
      to: "src/services/market_data.py"
      via: "mocked yfinance calls"
---

<objective>
Increase unit test coverage for the service layer and graph utilities, achieving 100% path coverage for financial math functions using property-based testing (Hypothesis) and ensuring resilience against external API failures.
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
@src/services/portfolio.py
@src/services/market_data.py
@src/graph/utils/prompt.py
@src/graph/utils/news.py
@src/graph/utils/agents.py
@src/graph/utils/tool_call.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Portfolio Math Property-Based Testing</name>
  <files>tests/unit/services/test_portfolio_math.py</files>
  <action>
    Create a new test file using `hypothesis` to perform property-based testing for all math functions in `src/services/portfolio.py`.
    
    Implementation details:
    - Use `st.decimals` for monetary values and quantities.
    - Test `calculate_new_acb`: Verify that new ACB is weighted average, handles zero-division safety, and never results in negative values for valid BUYs.
    - Test `calculate_gain_loss` and `calculate_daily_pnl`: Verify percentage calculations and zero-division handling for start values.
    - Test `process_transactions_chronologically`: Use `st.lists` of transactions. Verify that it correctly identifies sequences leading to negative holdings (raising 400 HTTPException) and accurately maintains ACB across BUY/SELL cycles.
    
    Target: 100% path coverage for the targeted functions.
  </action>
  <verify>
    Run `pytest --cov=src/services/portfolio --cov-branch tests/unit/services/test_portfolio_math.py`
  </verify>
  <done>
    `pytest-cov` reports 100% branch coverage for `calculate_new_acb`, `calculate_gain_loss`, `calculate_daily_pnl`, and `process_transactions_chronologically` in `portfolio.py`.
  </done>
</task>

<task type="auto">
  <name>Task 2: Market Data Resilience & Caching</name>
  <files>tests/unit/services/test_market_data.py</files>
  <action>
    Implement unit tests for `src/services/market_data.py` focusing on fault tolerance and caching.
    
    Tests to include:
    - `get_historical_fx_rate`: Mock `yfinance` to simulate network errors and empty history. Verify fallback to cache and then to Decimal("1.0").
    - `get_current_price`: Mock `ticker.fast_info` and `ticker.history`. Verify it tries both and falls back to the last transaction price from DB if both fail.
    - `_parse_yf_news_item`: Test with both the new `content` structure (with `clickThroughUrl`) and the legacy `title`/`link` structure.
    - `fetch_yfinance_news_urls`: Verify it collects and filters news items correctly.
    - `validate_transaction_price`: Test behavior when yfinance returns no data (should return True/pass).
  </action>
  <verify>
    Run `pytest tests/unit/services/test_market_data.py`
  </verify>
  <done>
    Market data service tests pass, covering edge cases where external data is missing or malformed.
  </done>
</task>

<task type="auto">
  <name>Task 3: Graph Utility Robustness</name>
  <files>tests/unit/utils/test_graph_utils.py</files>
  <action>
    Implement unit tests for utility functions used within the LangGraph workflow.
    
    Target modules:
    - `src/graph/utils/prompt.py`: Test `convert_state_to_prompt` with complex `AgentState` scenarios: empty history, mixed message types (BaseMessage vs tuples), missing `session_context` or `user_context`.
    - `src/graph/utils/agents.py`: Verify `get_next_interaction_id` and the `with_logging` decorator (ensure it correctly logs starting/stopping and re-raises exceptions).
    - `src/graph/utils/news.py`: Mock `httpx` to test `fetch_article_content` with 404/500 status codes, timeouts, and malformed HTML. Test `get_summary_result` mapping.
  </action>
  <verify>
    Run `pytest tests/unit/utils/test_graph_utils.py`
  </verify>
  <done>
    All utility functions handle edge cases in state and external data without crashing, ensuring stable graph execution.
  </done>
</task>

</tasks>

<verification>
Run the full suite of unit tests created in this plan:
`pytest tests/unit/services/ tests/unit/utils/`
Check coverage:
`pytest --cov=src/services --cov=src/graph/utils tests/unit/`
</verification>

<success_criteria>
- 100% path coverage for financial math functions in `src/services/portfolio.py`.
- 0 failures in service and utility unit tests.
- Graceful handling of external API failures (yfinance, news fetching).
</success_criteria>

<output>
After completion, create `.planning/phases/phase-8/8-01-SUMMARY.md`
</output>
