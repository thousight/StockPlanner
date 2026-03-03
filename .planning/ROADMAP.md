# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone History
- [v1: API Server & Cloud Sync](.planning/milestones/v1-ROADMAP.md) — Established async foundation, LangGraph persistence, and financial CRUD. (Completed 2026-03-02)

## Milestone 2: Basic Authentication & User Management (Current)
**Goal:** Establish a complete authentication flow via APIs, including user persistence and JWT protection.

| Phase | Title | Focus | Status |
|---|---|---|---|
| **Phase 9** | **User Foundation** | User table, password hashing, and Sign-Up API. | Completed |
| **Phase 10** | **JWT Authentication** | Sign-In API, JWT generation, and Auth Middleware. | Completed |
| **Phase 11** | **Authenticated Isolation** | Refactor all APIs to use JWT user context. | Completed |

### Phase 9: User Foundation
**Goal:** Implement the database-level user model and the initial registration flow.
**Plans:** 3 plans

**Requirements:** REQ-040, REQ-041, REQ-042

**Plans:**
- [x] 9-01-PLAN.md — User Schema & Password Hashing (UUIDv7, Argon2id).
- [x] 9-02-PLAN.md — Sign-Up API & Profile Logic.
- [x] 9-03-PLAN.md — User Management Unit Tests.

### Phase 10: JWT Authentication
**Goal:** Implement login logic, JWT issuance, and a robust FastAPI dependency for authentication.
**Plans:** 3 plans

**Requirements:** REQ-043, REQ-050, REQ-051, REQ-052, REQ-053

**Plans:**
- [x] 10-01-PLAN.md — JWT Core & Sign-In API (Access Tokens).
- [x] 10-02-PLAN.md — Refresh Token Rotation & Session Management.
- [x] 10-03-PLAN.md — Auth Dependency & Security Verification.

### Phase 11: Authenticated Isolation
**Goal:** Migrating existing Financial and Chat endpoints to strictly enforce user isolation based on JWT sub claims.
**Plans:** 3 plans

**Requirements:** REQ-060, REQ-061, REQ-062

**Plans:**
- [x] 11-01-PLAN.md — Portfolio & Transaction Isolation Refactor. (Renamed to Legacy Data Migration)
- [x] 11-02-PLAN.md — Chat Thread & Persistence Ownership. (Renamed to Context Propagation & Controller Refactor)
- [x] 11-03-PLAN.md — Multi-User E2E Integration Tests. (Renamed to LangGraph Profile Injection & Multi-User Verification)

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

## Milestone 6: OAuth & Google Sign-In
**Goal:** Expand authentication options for better mobile onboarding.
- Integration with Google Identity Services.
- Account linking between basic auth and Google accounts.
