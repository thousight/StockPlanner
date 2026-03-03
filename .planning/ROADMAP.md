# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone History
- [v1: API Server & Cloud Sync](.planning/milestones/v1-ROADMAP.md) — Established async foundation, LangGraph persistence, and financial CRUD. (Completed 2026-03-02)

## Milestone 2: Authentication & User Isolation (Current)
**Goal:** Secure the API and ensure individual users can safely manage their own financial data.

| Phase | Title | Focus | Status |
|---|---|---|---|
| **Phase 9** | **Auth Scaffolding** | Setup Google Sign-in and JWT verification. | Pending |
| **Phase 10** | **User Isolation** | Schema updates and row-level security logic. | Pending |

### Phase 9: Auth Scaffolding
**Goal:** Setup Google Sign-in integration and JWT-based authentication middleware.
**Plans:** [To be planned]

### Phase 10: User Isolation
**Goal:** Update database schemas and API logic to ensure data is strictly isolated by user ID.
**Plans:** [To be planned]

## Milestone 3: Conversation History & Memory
**Goal:** Enhance the user experience with persistent chat history and fast short-term memory.
- Redis integration for short-term conversation state.
- Permanent storage for user-agent dialogue history.
- API endpoints to fetch and manage conversation logs.

## Milestone 4: Advanced Agents & Financial Context
**Goal:** Deepen the analytical capabilities of the agentic team.
- Specialized agents for EDGAR (SEC filings) and social media analysis.
- Narrative and sentiment analysis for news articles.
- Refactored agent architecture for better modularity and streaming stability.

## Milestone 5: Daily Proactive Analysis
**Goal:** Move from reactive chat to proactive financial coaching.
- Deep research agents for comprehensive news scraping.
- Automated daily portfolio reviews and personalized summary generation.
