# Phase 20 Research: Market Narrative & Sentiment Change Agent

## Standard Stack
- **Trading Calendar:** `pandas_market_calendars` (specifically the `NYSE` calendar) for robust trading day calculations.
- **Market Data:** `yfinance` for fetching index prices (SPY, QQQ, DIA, VIX).
- **Search:** `DuckDuckGo Search` (via `web_search` tool) with targeted domain filters (Bloomberg, WSJ, Reuters, CNBC).
- **Orchestration:** `LangGraph` for agent state management and supervisor routing.
- **LLM:** `gpt-4o` for narrative synthesis and `gpt-4o-mini` for structured sentiment extraction.

## Architecture Patterns
- **Standalone Researcher:** The `NarrativeResearcher` is a high-level specialist that synthesizes data from multiple tools (Price, Macro, News) into a cohesive "Market Pulse."
- **State Injection:** The agent's output is injected into `AgentState.market_context` to provide global awareness for other agents.
- **Comparison Logic:** Uses a "Lookback-and-Compare" pattern:
    1. Fetch current narrative.
    2. Retrieve last known narrative from `ResearchCache` (up to 7 days back).
    3. LLM compares the two to identify shifts in the "Top 3 Narrative Drivers."
- **Key-Value Indexing:** Uses `narrative_YYYYMMDD` keys in `ResearchCache` for efficient daily retrieval.

## Don't Hand-Roll
- **Trading Day Math:** NEVER use simple `timedelta(days=1)` logic. Always use `pandas_market_calendars` to handle weekends, early closures, and holidays.
- **Search Result Filtering:** Use the `site:` operator in search queries rather than manually filtering a large list of general news results.
- **Sentiment Scoring:** Use the existing `analyze_sentiment` tool logic to ensure consistency across the platform.

## Common Pitfalls
- **Timezone Mismatches:** `pandas_market_calendars` returns UTC. Ensure conversion to `America/New_York` for NYSE-relevant logic.
- **Empty Search Results:** Professional paywalls (WSJ/Bloomberg) can sometimes lead to empty search snippets. Implement fallbacks to `yfinance` news if `web_search` fails.
- **Cache Overwrite:** Ensure that `narrative_YYYYMMDD` is only written once per day or updated carefully to avoid losing the "initial" morning narrative vs. the "closing" narrative.

## Code Examples

### 1. Robust Previous Trading Day Logic
```python
import pandas_market_calendars as mcal
from datetime import datetime, timedelta

def get_previous_trading_day(target_date: datetime):
    nyse = mcal.get_calendar('NYSE')
    # Look back 10 days to guarantee finding a session
    valid_days = nyse.valid_days(
        start_date=target_date - timedelta(days=10),
        end_date=target_date - timedelta(days=1)
    )
    return valid_days[-1].date()
```

### 2. Narrative Search Query Pattern
```python
search_query = '(site:bloomberg.com OR site:wsj.com OR site:reuters.com OR site:cnbc.com) "market recap" OR "closing bell" after:2024-03-05'
```

### 3. Structured Narrative Shift Schema
```python
class NarrativeShift(BaseModel):
    current_narrative: str
    previous_narrative: Optional[str]
    top_3_drivers: List[str]
    sentiment_shift: str  # e.g., "Pivot from Inflation to Growth"
    confidence: float
```

## Confidence Levels
- **Trading Day Logic:** High (Industry standard library).
- **Search Reliability:** Medium (Depends on paywalls and search quality).
- **Narrative Synthesis:** High (GPT-4o performs well on high-level synthesis).
