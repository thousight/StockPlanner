# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone History
- [v1: API Server & Cloud Sync](.planning/milestones/v1-ROADMAP.md) — Established async foundation, LangGraph persistence, and financial CRUD. (Completed 2026-03-02)
- [v2: Basic Authentication & User Management](.planning/milestones/v2-ROADMAP.md) — Established JWT security flow and multi-tenant data isolation. (Completed 2026-03-02)
- [v3: Conversation History & Memory](.planning/milestones/v3-ROADMAP.md) — Established Redis memory and permanent history storage. (Completed 2026-03-03)

## Milestone 4: Advanced Agents & Financial Context (Current)
**Goal:** Deepen the analytical capabilities of the agentic team.

- Specialized agents for EDGAR (SEC filings) and social media analysis.
- Narrative and sentiment analysis for news articles.
- Refactored agent architecture for better modularity and streaming stability.

### Phase 15: SEC & EDGAR Agent
**Goal:** Dedicated agent for parsing SEC filings and structured reports.
**Status:** Completed

### Phase 16: Social & Sentiment
**Goal:** Analysis of social media trends and news sentiment.
**Status:** Completed

### Phase 17: Modular Graph
**Goal:** Refactoring the supervisor graph for specialized analyst routing.
**Status:** Completed

### Phase 18: Macro Economics Tracking
**Goal:** Dedicated tools and agents for tracking expanded macro-economic indicators.
**Status:** Completed

### Phase 19: Free Macro Data & Caching
**Goal:** Switch to free macro data alternative (remove Finnhub) and implement ResearchCache for all macro services.
**Status:** Completed

## Milestone 5: Daily Proactive Analysis
**Goal:** Move from reactive chat to proactive financial coaching.
- Deep research agents for comprehensive news scraping.
- Automated daily portfolio reviews and personalized summary generation.

## Milestone 6: OAuth & Google Sign-In
**Goal:** Expand authentication options for better mobile onboarding.
- Integration with Google Identity Services.
- Account linking between basic auth and Google accounts.
