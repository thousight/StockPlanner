# Phase 18 Context: Macro Economics Tracking

## Overview
This phase implements a comprehensive macro-economic tracking system. It introduces official data sourcing via the FRED API, adds an economic calendar, and refactors the caching mechanism to allow agents to dynamically control data expiration. The `MacroResearcher` will now provide essential context for all investment theses.

## Implementation Decisions

### 1. Macro Indicator Scope (US Market Focus)
- **Hard Data:** GDP Growth, US Dollar Index (DXY), CPI/Inflation, FOMC/Interest Rates, Non-Farm Payrolls (Employment).
- **Market Context:** Sector-wide performances and Key Commodities (Oil, Brent, Gold, Natural Gas).
- **Thematic Grouping:** Reports must group findings into themes (e.g., "The Inflation Pulse," "Labor Market Dynamics," "Energy & Commodities").
- **Lookback:** Use a standard **6-month window** to identify trends and "Rate of Change."
- **Alerts:** Explicitly highlight if any indicator reaches a **Multi-year High or Low**.

### 2. Sourcing & Tools
- **FRED Integration:** Create `src/services/macro.py` to interface with the Federal Reserve Economic Data API for authoritative time-series data.
- **Economic Calendar:** Implement a tool to fetch upcoming high-impact economic events (CPI release dates, FOMC meetings).
- **Narrative Augmentation:** Use `web_search` to find "the why" behind the numbers (e.g., policy shifts or geopolitical triggers).
- **Output:** The `MacroResearcher` produces a **Narrative Report** intended for the `AnalystAgent`, focusing on context rather than just raw tables.

### 3. Dynamic Cache Refactor (CRITICAL)
- **Agent-Driven TTL:** Refactor the news and research fetching mechanism. Instead of tools/utils hardcoding a 24h or 7-day TTL, the **Agent** (or the summarization logic) will decide the `expire_at` value based on the data's relevance.
- **Implementation:** Tools like `get_summary`, `analyze_sentiment`, and `get_sec_filing_section` must be updated to accept a dynamic TTL/expiry parameter.

### 4. Orchestration & Priority
- **Automated Trigger:** The `Supervisor` will now **always** trigger the `MacroResearcher` for stock-related queries to ensure thebackdrop is established.
- **Thesis Hierarchy:** In conflicts, **Fundamentals (SEC/10-K) > Macro Trends**. Macro is used as the "ceiling" or "tailwind," but company-specific data has the final say.
- **Sector Sensitivity:** Analysts will dynamically weight macro impact based on the "events of the day" (e.g., a sudden rate spike affecting Real Estate more than Tech).

## Code Context
- **Services:** New `src/services/macro.py` (FRED).
- **Tools:** Update `src/graph/tools/news.py` and `src/graph/tools/sec.py` for dynamic TTL.
- **Agents:** Update `MacroResearcher` logic and `Supervisor` trigger logic.
- **Database:** No schema changes needed (ResearchCache already supports `expire_at`).

## Deferred Ideas (Out of Scope)
- Global macro indicators (EU, China, etc.).
- Numerical "Economy Sentiment Score" (sticking to narrative logic for now).
