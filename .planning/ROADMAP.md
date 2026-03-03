# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone History
- [v1: API Server & Cloud Sync](.planning/milestones/v1-ROADMAP.md) — Established async foundation, LangGraph persistence, and financial CRUD. (Completed 2026-03-02)
- [v2: Basic Authentication & User Management](.planning/milestones/v2-ROADMAP.md) — Established JWT security flow and multi-tenant data isolation. (Completed 2026-03-02)

## Milestone 3: Conversation History & Memory (Current)
**Goal:** Enhance the user experience with persistent chat history and fast short-term memory.

| Phase | Title | Focus | Status |
|---|---|---|---|
| **Phase 12** | **Memory Refactor** | Redis integration for short-term conversation state. | Pending |
| **Phase 13** | **History Management** | Permanent storage and management APIs for chat logs. | Pending |

### Phase 12: Memory Refactor
**Goal:** Integrate Redis to provide high-speed, short-term memory for agentic workflows.
**Plans:** [To be planned]

### Phase 13: History Management
**Goal:** Implement permanent database storage for all user-agent interactions and expose retrieval APIs.
**Plans:** [To be planned]

## Milestone 4: Advanced Agents & Financial Context
**Goal:** Deepen the analytical capabilities of the agentic team.
- Specialized agents for EDGAR (SEC filings) and social media analysis.
- Narrative and sentiment analysis for news articles.
- Refactored agent architecture for better modularity and streaming stability.

## Milestone 5: Daily Proactive Analysis
**Goal:** Move from reactive chat to proactive financial coaching.
- Deep research agents for comprehensive news scraping.
- Automated daily portfolio reviews and personalized summary generation.

## Milestone 6: OAuth & Google Sign-In
**Goal:** Expand authentication options for better mobile onboarding.
- Integration with Google Identity Services.
- Account linking between basic auth and Google accounts.
