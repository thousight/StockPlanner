# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone 1: API Server & Cloud Sync (Current)
**Goal:** Establish the foundation for a RESTful, cloud-powered backend with real-time agent streaming.

| Phase | Title | Focus | Status |
|---|---|---|---|
| **Phase 1** | **API Scaffolding** | Setup FastAPI, health checks, and async architecture. | Completed |
| **Phase 2** | **Data & Persistence** | Railway integration, PostgreSQL schemas, and LangGraph checkpointer. | Completed |
| **Phase 3** | **Financial APIs** | Portfolio analytics and transaction CRUD operations. | Completed |
| **Phase 4** | **Agentic Chat Streaming** | Streaming SSE `/chat` endpoint and thread management. | Completed |
| **Phase 5** | **Agentic Flow Refinement** | Conditional interrupts and report commit optimization. | Completed |
| **Phase 6** | **Test Coverage** | Comprehensive unit and integration testing. | Completed |

### Phase 1: API Scaffolding
**Goal:** Setup FastAPI, health checks, and async architecture for a Railway-hosted PostgreSQL backend.
**Plans:** 3 plans

**Requirements:** REQ-001, REQ-002, REQ-003, REQ-020, REQ-023, REQ-030

**Plans:**
- [x] 1-01-PLAN.md — Reorganize project structure and setup dependencies.
- [x] 1-02-PLAN.md — Implement core FastAPI infrastructure and middleware.
- [x] 1-03-PLAN.md — Implement async database and health diagnostics.

### Phase 2: Data & Persistence
**Goal:** Finalize PostgreSQL schemas, implement Alembic migrations, LangGraph checkpointer, and automated data lifecycle.
**Plans:** 3 plans

**Requirements:** REQ-012, REQ-020, REQ-023

**Plans:**
- [x] 2-01-PLAN.md — Schema Foundation & Migrations (Alembic async, Reports table).
- [x] 2-02-PLAN.md — Persistence & Lifecycle (AsyncPostgresSaver, APScheduler TTL).
- [x] 2-03-PLAN.md — Transaction Integrity (Propose-Commit pattern, concurrency).

### Phase 3: Financial APIs
**Goal:** Implement portfolio analytics and transaction CRUD operations with multi-currency support, fractional shares, and strict consistency.
**Plans:** 3 plans

**Requirements:** REQ-021, REQ-022, REQ-023

**Plans:**
- [x] 3-01-PLAN.md — Refine Financial Schema & Polymorphic Metadata.
- [x] 3-02-PLAN.md — Transaction CRUD with Strict Consistency & FX.
- [x] 3-03-PLAN.md — Portfolio Analytics & Performance Metrics.

### Phase 4: Agentic Chat Streaming
**Goal:** Implement real-time SSE chat endpoint, LangGraph multi-agent orchestration integration, and human-in-the-loop patterns.
**Plans:** 4 plans

**Requirements:** REQ-010, REQ-011, REQ-012, REQ-013

**Plans:**
- [x] 4-01-PLAN.md — Persistence & Graph Orchestration (AsyncPostgresSaver, Context Injection).
- [x] 4-02-PLAN.md — Streaming Chat Core (FastAPI /chat, SSE Generator, Disconnect Handling).
- [x] 4-03-PLAN.md — Thread Lifecycle & History (Auto-Titling, Paginated History API).
- [x] 4-04-PLAN.md — Human-in-the-Loop & Interrupts (Safety Breakpoints, Resume Endpoint).

### Phase 5: Agentic Flow Refinement
**Goal:** Make breakpoints conditional and optimize the report committing process to improve UX for non-financial chats.
**Plans:** 3 plans

**Requirements:** REQ-011, REQ-013

**Plans:**
- [x] 5-01-PLAN.md — Data Foundation & Search API.
- [x] 5-02-PLAN.md — Complexity Analysis & Metadata Logic.
- [x] 5-03-PLAN.md — Conditional Flow & SSE Refinement.

### Phase 6: Test Coverage
**Goal:** Implement a comprehensive testing suite covering core financial logic, API endpoints, and agentic workflows.
**Plans:** 4 plans

**Requirements:** REQ-032

**Plans:**
- [x] 6-01-PLAN.md — Foundation & Financial Logic.
- [x] 6-02-PLAN.md — Mocking & Database Layer.
- [x] 6-03-PLAN.md — API CRUD & Integration.
- [x] 6-04-PLAN.md — SSE Streaming & Agent Resilience.

## Milestone 2: Authentication & User Isolation
**Goal:** Secure the API and ensure individual users can safely manage their own financial data.
- Google Sign-in integration.
- JWT-based authentication for all endpoints.
- Database schema updates to isolate user-specific data.

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
