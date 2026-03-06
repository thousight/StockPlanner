# Phase 19 Context: Free Macro Data & Caching

## Overview
This phase stabilizes the macro-economic data pipeline by removing the restricted Finnhub service and replacing it with a reliable free-tier API (Financial Modeling Prep). It also unifies all macro caching into the `ResearchCache` at the Tool level, using a date-based indexing strategy and dynamic expiration.

## Implementation Decisions

### 1. Alternative Economic Calendar (Financial Modeling Prep)
- **Source:** Replace Finnhub with the **Financial Modeling Prep (FMP) API**.
- **Service Name:** Keep the generic `EconomicCalendarService` class name in `src/services/macro.py` but update the internal logic to use FMP.
- **Fields:** Ensure the new service captures `event`, `estimate`, `previous`, and `actual`.
- **Fallback:** If FMP fails or returns empty, the `MacroResearcher` must use `web_search` to find the "US economic calendar for [current_week]" as a live fallback.
- **Mock Data:** Keep `_get_mock_calendar_data` as a final safety fallback.

### 2. Caching Architecture (Tool Level)
- **Granularity:** Cache the **Final Formatted Narrative report** at the Tool level (`get_key_macro_indicators`). This avoids re-summarizing or re-formatting hard data within the same day.
- **Key Schema:** Use a date-based key format: `macro_YYYYMMDD` (e.g., `macro_20260305`). This ensures a clean daily slate.
- **Persistence:** All macro reports will be stored in `ResearchCache` with `source_type="MACRO"`.

### 3. Dynamic Expiration & Invalidation
- **Next-Event Invalidation:** For the Economic Calendar, the `expire_at` timestamp should be set to the **exact time of the next high-impact event** identified in the fetch.
- **Default TTL:** 
    - **Macro Hard Data:** Expire at end of current day (midnight) or next event.
    - **News/Social:** Default to **24 hours** if not specified by an agent.
- **Black Swan Override:** If the `SentimentResearcher` detects a "Black Swan" or "High Volatility" event (massive sentiment shift), it will set a `refresh_macro` flag in the `AgentState`. The `MacroResearcher` will honor this flag by ignoring the cache and forcing a fresh fetch.

### 4. Code Cleanup
- **Purge Finnhub:** Remove `FINNHUB_API_KEY` from `src/config.py`, all `.env` templates, and UAT scripts.
- **Sync:** Update `src/services/macro.py` and `src/graph/tools/macro.py` to support the new caching and sourcing logic.

## Code Context
- **Services:** `src/services/macro.py` (FMP implementation).
- **Tools:** `src/graph/tools/macro.py` (Implementation of `macro_YYYYMMDD` caching).
- **Utilities:** `src/graph/utils/news.py` (24hr default TTL).
- **State:** `src/graph/state.py` (Potential `refresh_macro` boolean flag).

## Deferred Ideas (Out of Scope)
- Historical macro time-series visualization (sticking to narrative reports).
- International economic calendars (US focus only).
