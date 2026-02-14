# Roadmap

## Phase 1: Foundation (Data & Supervisor)
**Goal:** Establish the LangGraph supervisor architecture and prove accurate data retrieval.
- [ ] **Infrastructure Setup:** Project structure, poetry/pip env, API key management.
- [ ] **Market Data Agent:** Implement `PriceFetcher` using Finnhub.
- [ ] **Supervisor Node:** Implement basic routing logic (User -> Supervisor -> Market Agent).
- [ ] **Basic UI:** Simple Streamlit chat interface to test the graph.

## Phase 2: Education Engine (News & ELI5)
**Goal:** Implement the core value proposition—simplifying financial data.
- [ ] **News Agent:** Implement `NewsFetcher` (DuckDuckGo/Finnhub News).
- [ ] **Explanation Agent:** Implement the "ELI5" re-writing logic (Editor node).
- [ ] **Integration:** Update Supervisor to route "Why?" questions to News -> Explanation.
- [ ] **Prompt Tuning:** Refine "Explain Like I'm 5" metaphors for target audience.

## Phase 3: Portfolio & Planning
**Goal:** Add personalization and context.
- [ ] **Database Layer:** SQLite models for `Portfolio` and `Transaction`.
- [ ] **Portfolio Agent:** Tools to Add/View/Analyze holdings.
- [ ] **Planner Agent:** Logic for "Am I on track?" (Age/Risk heuristics).
- [ ] **Dashboard UI:** Add visual portfolio summary to Streamlit.

## Phase 4: Polish & Compliance
**Goal:** Prepare for user release (even if local).
- [ ] **Compliance Guardrails:** Add system prompt injections for disclaimers.
- [ ] **Accessibility Review:** Check font sizes, contrast, and clarity.
- [ ] **Error Handling:** Graceful failures when APIs are down.
- [ ] **Documentation:** User guide for "How to run".
