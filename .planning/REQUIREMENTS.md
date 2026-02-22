# Requirements

## 1. Multi-Agent Refactor (Architecture)
- [ ] **Supervisor Node:** Implement a central planner node that receives user intent and delegates to specialized workers.
- [ ] **Worker Pattern:** Define a standard `AgentWorker` interface (or skill) for data retrieval and analysis nodes.
- [ ] **Tooling Wrapper:** Wrap existing tools (`yfinance`, `duckduckgo`) into standardized Agent Tools.
- [ ] **Parallel Execution:** Enable the supervisor to trigger multiple worker nodes in parallel (e.g., Financials + News) using LangGraph's branching logic.

## 2. Deep Stock Profiling (Issue #5)
- [ ] **Business Profile:** Fetch and summarize company basics, revenue drivers, and competitive landscape.
- [ ] **Financial Health:** Automated retrieval of 1y/3y/5y CAGR, margins, debt ratios, and ROE/ROIC.
- [ ] **Valuation Metrics:** Automated calculation of P/E, EV/EBITDA, and PEG vs. historical averages.
- [ ] **Dividend Policy:** Analysis of payout ratios and historical consistency.

## 3. Whale Tracking (Issue #3)
- [ ] **EDGAR Scraper:** Implement a scraper to fetch and parse SEC 13F filings for specific tickers.
- [ ] **Institutional Context:** Summarize top 10 institutional holders and recent big moves (buys/sells) to inform the final analysis report.

## 4. Narrative Intelligence (Issue #2)
- [ ] **Sentiment Hybrid:** Correlate news sentiment spikes with social media (Reddit/X) volume to flag artificial hype bubbles.
- [ ] **Hype Detection:** Logic to assess if current price volatility is "story-driven" (narrative) vs. "fact-driven" (fundamentals).

## 5. User Alignment (Issue #1)
- [ ] **Formal Profiling:** Implement a one-time setup flow to capture User Age, Risk Tolerance (Conservative/Moderate/Aggressive), and Goals.
- [ ] **Alignment Scorer:** A final "Editor" node that scores the analyzed stock against the user's profile and flags discrepancies (e.g., "Too volatile for your conservative profile").

## 6. Technical & UX
- [ ] **Database Persistence:** Enhance SQLite models to cache stock profiles and institutional snapshots.
- [ ] **Streamlit UI:**
  - [ ] **Portfolio Management:** Add/Edit/Delete holdings.
  - [ ] **Analysis Report:** A clean, multi-section markdown report rendered in Streamlit.
- [ ] **API Security:** Secure management of OpenAI and other API keys via `.env`.
