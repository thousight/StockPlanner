# Roadmap

## Phase 1: Multi-Agent Core Refactor (Architecture) [COMPLETED]
**Goal:** Establish the LangGraph supervisor/agent architecture and migrate existing research logic.
- [x] **Infrastructure Setup:** Finalize project structure and dependency management.
- [x] **Supervisor Agent:** Implement the `SupervisorAgent` with planning and routing logic.
- [x] **Financials Agent:** Implement a agent for basic stock data and financials (yfinance).
- [x] **News Agent:** Implement a agent for news and basic sentiment (DuckDuckGo).
- [x] **Integration:** Connect the Supervisor to agents and test the graph.
- [x] **Basic UI:** Update Streamlit to trigger the multi-agent graph and show agent "thinking" steps.

## Phase 2: Deep Profiling & Whale Tracking (Data Intelligence)
**Goal:** Implement the "Deep Stock Profile" and track institutional movements.
- [ ] **Deep Profile Agent:** Add business model, competitive landscape, and historical financials (Issue #5).
- [ ] **EDGAR Scraper (Whale Tracker):** Implement the 13F filing scraper and parser for institutional context (Issue #3).
- [ ] **Valuation Logic:** Build the agent that calculates and compares multiples (P/E, EV/EBITDA, etc.).
- [ ] **Database Persistence:** Cache deep profiles and institutional snapshots in SQLite.

## Phase 3: Narrative Intelligence (Market Hype)
**Goal:** Implement the hybrid detection of narratives and "Hype" bubbles.
- [ ] **Social Agent:** Implement a agent to scrape/analyze sentiment from Reddit/X (Issue #2).
- [ ] **Hype Detector Agent:** Logic to correlate sentiment spikes with news and price action.
- [ ] **Narrative Analysis:** Summarize if current market moves are driven by artificial stories or fundamentals.

## Phase 4: User Alignment & Final Reporting
**Goal:** Personalize analysis and polish the user experience.
- [ ] **Formal Setup Flow:** Implement the UI to capture user profile (Age, Risk, Goals) (Issue #1).
- [ ] **Alignment Scorer (Editor):** Create the final agent that flags if a stock matches the user's profile.
- [ ] **Full Analysis UI:** Multi-tab report in Streamlit (Summary, Financials, Whale Context, Narrative, User Fit).
- [ ] **Refinement:** Polish prompts and error handling for all agents.

## Phase 5: Generic Personal Assistant
**Goal:** Generalize the platform beyond finance into a holistic decision-support system.
- [ ] **Domain Expansion:** Refactor Researcher/Analyst agents to handle non-financial queries (travel, health, productivity).
- [ ] **Enhanced Profiling:** Expand user profile to capture hobbies, interests, and life goals.
- [ ] **Adaptive UI:** Create a dynamic interface that adjusts based on the query domain.
