# Phase 20 Context: Market Narrative & Sentiment Change Agent

## Overview
This phase implements a specialized `NarrativeResearcher` agent that synthesizes market price action (Indices/VIX), macro data, and professional news recaps into a "Market Narrative of the Day." Crucially, it retrieves the last known narrative (up to 7 days back) to identify and explain shifts in the top 3 narrative drivers.

## Implementation Decisions

### 1. Narrative Construction (The "Market Pulse")
- **Anchors:** Uses `SPY`, `QQQ`, `DIA` for direction and `VIX` for sentiment/fear context.
- **Sources:** Prioritizes `yfinance` for price action, `FRED` for yields/macro, and `web_search` (filtering for WSJ, Bloomberg, Reuters, CNBC) for professional narrative summaries.
- **Friction:** If data conflicts (e.g., "Indices up on bad macro data"), the agent must explicitly state the conflict rather than smoothing it over.
- **Independence:** The agent is autonomous and does not rely on calling the `MacroResearcher` or `SentimentResearcher` as sub-tasks; it uses the underlying tools/services directly.

### 2. Historical Comparison & Persistence
- **Schema Update:** Add `NARRATIVE` to `ResearchSourceType` and `ReportCategory` enums (Migration required).
- **Caching Strategy:**
    - **Key Format:** `narrative_YYYYMMDD` in `ResearchCache`.
    - **Lookup:** Look back up to **7 days** for the most recent "last known" record to compare against.
    - **TTL:** 24 hours or end of current trading day.
- **Comparison Focus:** Identifies the **Top 3 Narrative Drivers** from the previous record and compares them to today's drivers to calculate the "Narrative Shift."

### 3. Graph Integration & Routing
- **Routing Intent:** "What is the narrative driving [X] today?", "Why is the market moving like this?", "How has the market vibe changed?".
- **State Injection:** The calculated narrative summary is stored in `AgentState.market_context` so that subsequent agents (SEC, Analyst) have broad market awareness.
- **Response Mode:** The agent can provide a standalone final answer if the user query is purely narrative-focused.

## Code Context
- **Models:** `src/database/models.py` (Enum updates).
- **Agent:** `src/graph/agents/research/narrative.py` (New standalone agent).
- **Tools:** `src/graph/tools/narrative.py` (New tool for narrative synthesis and comparison logic).
- **Graph:** `src/graph/graph.py` (Supervisor routing and state injection).
- **State:** `src/graph/state.py` (Add `market_context` field).

## Deferred Ideas
- Real-time intraday narrative tracking (sticking to daily snapshots).
- Predictive narrative modeling (focusing on descriptive analysis first).
