# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone 1: API Server & Cloud Sync (Current)
**Goal:** Establish the foundation for a RESTful, cloud-powered backend with real-time agent streaming.

| Phase | Title | Focus | Status |
|---|---|---|---|
| **Phase 1** | **API Scaffolding** | Setup FastAPI, health checks, and async architecture. | Pending |
| **Phase 2** | **Data & Persistence** | Railway integration, PostgreSQL schemas, and LangGraph checkpointer. | Pending |
| **Phase 3** | **Financial APIs** | Portfolio analytics and transaction CRUD operations. | Pending |
| **Phase 4** | **Agentic Chat Streaming** | Streaming SSE `/chat` endpoint and thread management. | Pending |

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
