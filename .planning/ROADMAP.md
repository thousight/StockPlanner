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
**Goal:** Integrate Redis Stack to provide high-speed, short-term memory for agentic workflows using `AsyncRedisSaver`.
**Plans:** 3 plans

**Requirements:** REQ-070, REQ-071, REQ-072

**Plans:**
- [x] 12-01-PLAN.md — Redis Infrastructure & Lifespan Setup.
- [x] 12-02-PLAN.md — LangGraph Redis Checkpointer Migration.
- [ ] 12-03-PLAN.md — Legacy Cleanup & Migration.

### Phase 13: History Management
**Goal:** Implement permanent database storage for simplified user-agent interactions and expose retrieval APIs.
**Plans:** 3 plans

**Requirements:** REQ-080, REQ-081, REQ-082, REQ-090, REQ-091

**Plans:**
- [ ] 13-01-PLAN.md — Relational History Schema & Dual-Write Logic.
- [ ] 13-02-PLAN.md — History Retrieval & Management APIs.
- [ ] 13-03-PLAN.md — Memory & History Integration Verification.

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
