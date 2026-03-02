# Context - Phase 3: Financial APIs

This document captures implementation decisions for Phase 3 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Transaction Precision & Logic
- **Fractional Support:** The API must support fractional shares (e.g., 0.0001) for all asset types.
- **Fee Granularity:** Implement explicit fields for `commission` and `tax` rather than a single total fees field.
- **Multi-Currency:**
  - **Base Currency:** All portfolio reporting is converted to **USD**.
  - **Fallback Logic:** If a historical exchange rate is missing, the system will use the **nearest available date's rate**.
  - **Rate Source:** Manual overrides are not allowed at entry; the system will always use the **current spot rate** for the transaction date.
  - **Response Depth:** API responses must return both the **original currency/value** and the **converted base value**.
- **Price Validation:** Implement active validation against market data (yfinance or similar) to ensure entered prices are realistic for the given date.

## 2. Portfolio Analytics Depth
- **Performance metrics:** The primary focus for the MVP UI is **Daily Change** (value and percentage).
- **Breakdowns:** Include **Sector Allocation** analytics (e.g., % Tech, % Energy) in the portfolio response.
- **Cost Basis:** Use the **Average Cost** method for all portfolio performance and gain/loss calculations.
- **Benchmarking:** Provide a comparison metric against the **S&P 500 (SPY)** to show relative portfolio performance.

## 3. Asset-Specific Validation & Metadata
- **Real Estate:** Mandatory fields include **Type** (house, apartment, office, etc.), **Full Address**, and **Purchase Price**.
- **Private Equity / Funds:** Require detailed metadata including **Commitment Date** and **Vintage Year**.
- **Rare Metals:** Tracked via **Simple Quantity** (weight units are handled within the quantity field).
- **Generic Assets:** The system allows a "Generic" asset type with a custom name for non-standard investments.
- **Descriptions:**
  - **Requirement:** Optional for all non-stock assets.
  - **Format:** Plain Text only (max 500 characters).
  - **Visibility:** View-only metadata (not searchable).

## 4. Querying & Portfolio Integrity
- **Pagination:** Transaction history must be paginated (limit/offset) to support high-volume users on mobile.
- **Filtering:** Support comprehensive filtering by ticker, asset type (Stock, Real Estate, Fund, Metal, Generic), date range, and action.
- **Deletion:** Use **Soft Deletion** for all records to maintain audit trails.
- **Data Integrity:** Enforce **Strict Consistency**. Reject `SELL` transactions if there is insufficient "BUY" history to cover the quantity.
- **Non-Stock Pricing:** Prices for non-stock assets rely on the last transaction price, with architecture designed for future pricing API integration.
