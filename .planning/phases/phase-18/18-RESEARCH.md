# Phase 18 Research: Macro Economics Tracking

## 1. Authoritative Data Sourcing (FRED API)
- **Service Integration:** Implement a lightweight async `FREDService` using `httpx`.
- **Key Series IDs:**
  - **GDP Growth:** `A191RL1Q225SBEA` (Real GDP % Change, Quarterly).
  - **Inflation (CPI):** `CPIAUCSL` (Headline), `CPILFESL` (Core).
  - **Interest Rates:** `FEDFUNDS` (Effective Rate), `DFEDTARU`/`DFEDTARL` (Target Range).
  - **Employment:** `PAYEMS` (Non-Farm Payrolls), `UNRATE` (Unemployment Rate).
  - **US Dollar Index:** `DTWEXBGS` (Official Broad Index).
- **Update Frequency:**
  - GDP: Quarterly (with 3 estimates).
  - CPI/Payrolls: Monthly.
  - Rates: Daily/Post-meeting.

## 2. Economic Calendar
- **Source:** **Finnhub API** (Free tier: 60 calls/min) provides a dedicated `/calendar/economic` endpoint.
- **Filtering:** Focus on "High Impact" events for the US region to minimize noise.
- **Data Points:** Event Name, Country, Actual vs. Estimate, Impact Level.

## 3. Dynamic Cache TTL Refactor
- **Current State:** Hardcoded TTLs in `scraping.py` or tool wrappers.
- **New Architecture:**
  - Utilities like `get_summary` will accept an optional `expire_at: datetime` parameter.
  - The **Agent** (or its inner planner) decides the TTL based on data type:
    - **Macro (GDP):** 30 days (updates quarterly).
    - **News/Social:** 12-24 hours.
    - **High-Intensity Events:** 1-4 hours (during FOMC meetings).
- **Reducers:** No changes needed to `agent_interactions` as it already appends without overwriting.

## 4. Prompt Engineering (Thematic Reporting)
- **Structure:** Instead of a list of numbers, the `MacroResearcher` will be prompted to group data into:
  - **The Inflation Pulse** (CPI, DXY).
  - **Labor Market Dynamics** (Payrolls, UNRATE).
  - **Yields & Monetary Policy** (FEDFUNDS, 10Y Treasury).
- **Lookback:** Standardized to **6 months** to identify "Rate of Change" trends.
- **Thresholds:** Logic to flag multi-year highs/lows.

## 5. Market Context (Commodities & Sectors)
- **Tools:** Use `yfinance` for Key Commodities (`CL=F` for Oil, `GC=F` for Gold, `NG=F` for Natural Gas).
- **Sector ETFs:** Use proxies like `XLF` (Financials), `XLK` (Tech), `XLRE` (Real Estate) to establish sector-wide performance.
