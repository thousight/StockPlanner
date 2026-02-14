# Feature Landscape

**Domain:** Personal Financial Assistant (Beginner Focus)
**Researched:** 2024

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Stock Price Check** | Core function of any finance app. | Low | Use Finnhub Quote API. |
| **Portfolio Summary** | Users need to see "What do I own?" | Medium | Requires DB schema for user holdings + real-time valuation. |
| **Market News** | "Why is the market down?" | Medium | Aggregated news feed (Finnhub/NewsAPI). |
| **Chat Interface** | Natural language interaction. | High | The core AI value prop. |

## Differentiators

Features that set product apart for *Beginners* (Elderly/Young Adults).

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **"ELI5" Explanations** | Translates jargon (P/E ratio) into plain English metaphors. | High | Requires a dedicated "Editor" agent in the graph. |
| **Risk "Weather" Report** | Visual metaphor for volatility (Sunny = Safe, Stormy = Volatile). | Medium | Map VIX or Beta to icons/UI elements. |
| **Scam/Safety Check** | Analyzes "hot tips" for red flags. | High | "Is this crypto token safe?" -> checks liquidity/news. |
| **Voice Mode** | Accessibility for elderly; convenience for youth. | High | Text-to-Speech / Speech-to-Text integration. |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Auto-Trading** | High liability, complex compliance, dangerous for bugs. | Provide "Trade Instructions" to execute manually. |
| **"Buy" Signals** | Constitutes financial advice (regulated). | Provide "Analyst Consensus" data only. |
| **Crypto Gambling** | High risk for target demographic. | Focus on established assets (Stocks/ETFs). |

## Feature Dependencies

```
Stock Price Check → Portfolio Summary (Need prices to value portfolio)
Stock Price Check → Risk "Weather" Report (Need volatility data)
Chat Interface → "ELI5" Explanations (Chat output feeds into explanation layer)
```

## MVP Recommendation

Prioritize:
1.  **Chat Interface** with **Stock Price Check**.
2.  **"ELI5" Explanation Mode** (The killer feature for beginners).
3.  **Basic News Search** (Why is stock X moving?).

Defer: **Portfolio Summary** (Users may be hesitant to input data initially).

## Sources

- Competitor UX analysis (Robinhood vs. Fidelity vs. Acorns).
- Accessibility guidelines for elderly users (W3C WAI).
