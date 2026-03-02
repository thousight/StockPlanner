---
phase: 03-financial-apis
plan: 03
type: execute
wave: 3
depends_on: ["03-financial-apis-02"]
files_modified:
  - src/services/portfolio.py
  - src/main.py
  - src/services/benchmarking.py
autonomous: true
requirements: [REQ-021]

must_haves:
  truths:
    - "Portfolio metrics include Total Value, ACB, and Gain/Loss (USD)"
    - "Portfolio includes Sector Allocation breakdown"
    - "Portfolio is benchmarked against SPY"
    - "Daily Change (PNL) is calculated accurately, adjusting for cash flow"
  artifacts:
    - path: "src/services/portfolio.py"
      provides: "Aggregation and Sector analytics"
    - path: "src/services/benchmarking.py"
      provides: "SPY data and comparison logic"
  key_links:
    - from: "GET /investment"
      to: "Holding table"
      via: "Aggregation"
---

<objective>
Implement the Portfolio Analytics API to provide aggregated metrics, performance tracking, and benchmarking.

Purpose: Provide users with a high-level view of their portfolio performance and asset distribution.
Output: GET /investment endpoint with full performance and allocation data.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-3/3-CONTEXT.md
@.planning/phases/phase-3/3-RESEARCH.md
@.planning/phases/phase-3/3-02-PLAN.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Portfolio Aggregation API</name>
  <files>src/main.py, src/services/portfolio.py</files>
  <action>
    - Implement `get_portfolio_summary` service:
        - Aggregate all `Holdings` for the user.
        - Fetch current market prices for all assets (use cached daily snapshots if possible).
        - Calculate: `Total_Value_USD`, `Total_Cost_Basis_USD`, `Total_Gain_Loss_USD`, `Total_Gain_Loss_Pct`.
    - Implement `GET /investment` endpoint returning these metrics.
    - Ensure non-stock assets (Real Estate) use the last transaction price as the "current" price.
  </action>
  <verify>Perform manual verification by adding a few transactions and checking the `/investment` response for correct math.</verify>
  <done>Core portfolio metrics are calculated and exposed via the API.</done>
</task>

<task type="auto">
  <name>Task 2: Implement Performance & Allocation Analytics</name>
  <files>src/services/portfolio.py</files>
  <action>
    - Implement Sector Allocation: Group assets by `sector` (from Asset model) and calculate percentage of total portfolio value.
    - Implement Daily Change (PNL):
        - Use the formula: `Daily_PNL = Current_Value - (Value_At_Start_Of_Day + Net_Cash_Flow_Today)`.
        - Requires fetching `daily_snapshots` or calculating from transaction history.
  </action>
  <verify>Verify sector breakdown adds up to 100%. Test Daily PNL calculation with a deposit transaction to ensure it doesn't count as a "gain".</verify>
  <done>Users can see how their portfolio is distributed and its daily performance.</done>
</task>

<task type="auto">
  <name>Task 3: Implement SPY Benchmarking</name>
  <files>src/services/benchmarking.py</files>
  <action>
    - Implement `get_spy_performance`:
        - Fetch SPY historical data for the same period as the portfolio (using Alpaca or yfinance).
        - Cache SPY prices in a dedicated `BenchmarkCache` table.
    - Calculate relative performance: `Portfolio_Gain_Pct - SPY_Gain_Pct`.
    - Include benchmark data in the `GET /investment` response.
  </action>
  <verify>Check benchmarking logic against a known portfolio vs SPY scenario.</verify>
  <done>Portfolio performance is compared against the S&P 500 (SPY).</done>
</task>

</tasks>

<verification>
- Portfolio total value matches manual sum of holdings * prices.
- SPY benchmarking data is present and accurate.
- Sector allocation covers all assets.
</verification>

<success_criteria>
- `GET /investment` returns a JSON object with `total_value`, `gain_loss`, `sector_allocation`, and `benchmark_comparison`.
- All values are normalized to USD.
- Performance metrics accurately handle fractional shares.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-3/3-03-SUMMARY.md`
</output>
