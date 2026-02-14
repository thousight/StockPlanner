# Domain Pitfalls

**Domain:** Personal Financial Assistant
**Researched:** 2024

## Critical Pitfalls

### Pitfall 1: Hallucination of Financial Data
**What goes wrong:** LLM invents a stock price or P/E ratio that looks plausible but is wrong.
**Why it happens:** LLMs are probabilistic token predictors, not calculators.
**Consequences:** User loses money; absolute loss of trust.
**Prevention:** 
1. **Disable LLM math/knowledge for data.** Force tool usage for ALL numbers.
2. **Citation:** UI should link the number to the source (e.g., "Source: Finnhub").

### Pitfall 2: Crossing the "Advisory" Line
**What goes wrong:** The bot says "You should buy Tesla now."
**Why it happens:** LLMs mimic training data, which includes financial guru articles.
**Consequences:** Regulatory violation (SEC/FINRA), liability.
**Prevention:**
1. **System Prompt Injection:** "You are an educator. Never give personalized investment advice. Use phrases like 'analysts suggest' or 'historical data shows'."
2. **Disclaimer Footer:** Hardcoded on every screen.

### Pitfall 3: Latency & Stale Data
**What goes wrong:** User asks "Price of X", bot answers with yesterday's close because of API caching or limits.
**Prevention:** 
1. **Timestamping:** Always display *when* the data was fetched (e.g., "Data as of 10:00 AM").
2. **Clear Labels:** Mark data as "Real-time" vs "Delayed (15m)".

## Moderate Pitfalls

### Pitfall: Information Overload (The "Wall of Text")
**What goes wrong:** Bot returns a comprehensive 5-paragraph analysis to a 70-year-old beginner.
**Prevention:** "ELI5" post-processing layer. strict output formatting (bullets, short sentences).

### Pitfall: Ticker Confusion
**What goes wrong:** User asks for "Ford", bot gets "Forward Industries" instead of "Ford Motor Co".
**Prevention:** Validation step using a Symbol Lookup API before fetching quotes.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| **Phase 1 (Data)** | Rate Limiting | Implement caching decorator on all API tools immediately. |
| **Phase 2 (News)** | Sentiment Noise | Filter news for "Major" sources only; ignore blogspam which confuses sentiment analysis. |
| **Phase 3 (Planning)** | Bad Math | Use Python tools for all calculations (compound interest), never LLM math. |

## Sources

- SEC guidelines on "Robo-advisors".
- Common LLM failure modes in math/logic.
