# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone History
- [v1: API Server & Cloud Sync](.planning/milestones/v1-ROADMAP.md) — Established async foundation, LangGraph persistence, and financial CRUD. (Completed 2026-03-02)
- [v2: Basic Authentication & User Management](.planning/milestones/v2-ROADMAP.md) — Established JWT security flow and multi-tenant data isolation. (Completed 2026-03-02)
- [v3: Conversation History & Memory](.planning/milestones/v3-ROADMAP.md) — Established Redis memory and permanent history storage. (Completed 2026-03-03)
- [v4: Advanced Agents & Financial Context](.planning/milestones/v4-ROADMAP.md) — Specialized agents for SEC, social, and macro narrative. (Completed 2026-03-05)

## Milestone 5: Daily Proactive Analysis (Current)
**Goal:** Move from reactive chat to proactive financial coaching.
- [v5: Daily Proactive Analysis](.planning/milestones/v5-ROADMAP.md) — Deep research and automated portfolio briefings.

### Phase 21: Deep News Aggregator
**Goal:** Implement a robust news fetching system beyond standard `yfinance` and `ddgs`.
**Status:** In Progress

### Phase 22: Portfolio Performance & Benchmarking
**Goal:** Implementation of core daily performance metrics for users.
**Status:** Planned

### Phase 23: Daily Briefing Generator (MVP)
**Goal:** Create a unified engine for synthesizing daily reports.
**Status:** Planned

### Phase 24: Scheduled Jobs & Delivery
**Goal:** Automate the entire process for all users.
**Status:** Planned

## Milestone 6: OAuth & Google Sign-In
**Goal:** Expand authentication options for better mobile onboarding.
- Integration with Google Identity Services.
- Account linking between basic auth and Google accounts.
