# Plan Summary - Phase 3-03: Portfolio Analytics & Performance Metrics

## Implementation Summary
Successfully implemented the portfolio aggregation layer and real-time performance analytics. This fulfills REQ-021, providing users with a comprehensive view of their multi-asset holdings and market performance compared to key benchmarks.

- **Portfolio Aggregation:** Developed an efficient service to aggregate all user holdings, calculating total value, cost basis, and unrealized gains/losses in USD.
- **Daily Performance Logic:** Implemented daily gain/loss tracking using the formula: `Daily_PNL = Current_Value - (Value_At_Start_Of_Day + Net_Cash_Flow_Today)`. This accurately isolates market movement from user contributions (deposits/withdrawals).
- **Sector Allocation:** Added logic to group holdings by sector, providing a percentage-based breakdown of portfolio exposure across different industries.
- **SPY Benchmarking:** Created a benchmarking service that fetches S&P 500 (SPY) performance data, allowing users to compare their portfolio's YTD return against the broader market.
- **Asset Pricing Fallbacks:** Implemented a robust pricing strategy that uses `yfinance` for public stocks and falls back to the last recorded transaction price or manual appraisal for non-public assets (Real Estate, Funds).

## File Changes
- `src/services/portfolio.py`: Extended with `get_portfolio_summary` and daily performance calculation logic.
- `src/services/market_data.py`: Added `get_current_price` with asset-specific fallback logic.
- `src/services/benchmarking.py`: New service for fetching and calculating benchmark (SPY) performance.
- `src/controllers/portfolio.py`: New REST endpoint `GET /investment` for mobile dashboard data.
- `src/schemas/portfolio.py`: Pydantic schemas for structured portfolio analytics responses.
- `src/main.py`: Registered the portfolio analytics router.

## Technical Decisions
- **USD Reporting:** Standardized all portfolio-level analytics to USD, using real-time FX conversion where necessary to ensure consistent metrics across multi-currency holdings.
- **Net Cash Flow Adjustment:** Explicitly accounted for same-day transactions in the daily PNL calculation to prevent cash inflows (like buying more stock) from appearing as market gains.
- **On-the-fly Calculation:** Opted for dynamic calculation of portfolio summaries to ensure the Flutter client always sees the most recent market data, while ensuring efficient SQL queries to maintain performance.

## Verification
- Portfolio aggregation verified with multi-asset and multi-currency test data.
- Daily performance math verified against manual calculations including mid-day transactions.
- Benchmarking service confirmed to fetch accurate SPY data via `yfinance`.
- Pydantic schemas verified for correct nesting of allocation and performance metrics.
