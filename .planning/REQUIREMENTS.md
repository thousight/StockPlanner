# Requirements - Milestone 1: API Server & Cloud Sync

This milestone focuses on transforming the StockPlanner agent into a robust, cloud-synced RESTful API backend, ready to support a Flutter mobile frontend.

## 1. API Infrastructure

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-001** | **FastAPI Framework Implementation**: Implement a modern, asynchronous FastAPI server to replace the Streamlit interface. | P0 | Pending |
| **REQ-002** | **Asynchronous Architecture**: All API endpoints and agent nodes must be non-blocking (`async`/`await`) to support high-concurrency streaming. | P0 | Pending |
| **REQ-003** | **Health & Diagnostics**: Implement `/health` and `/docs` (Swagger) endpoints for monitoring and API discovery. | P1 | Pending |

## 2. Agentic Chat & Streaming

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-010** | **`/chat` Streaming Endpoint**: Implement a POST `/chat` endpoint that supports token-level streaming using Server-Sent Events (SSE). | P0 | Pending |
| **REQ-011** | **LangGraph Orchestration**: Integrate the existing multi-agent LangGraph workflow into the FastAPI request lifecycle. | P0 | Pending |
| **REQ-012** | **State Persistence (Checkpointer)**: Use `AsyncPostgresSaver` with Google Cloud SQL to persist conversation threads and agent states across requests. | P0 | Pending |
| **REQ-013** | **Thread Management**: Support `thread_id` in chat requests to allow multiple concurrent and persistent conversations. | P0 | Pending |

## 3. Financial Data & CRUD

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-020** | **Google Cloud SQL Integration**: Transition from local SQLite to a cloud-hosted Google Cloud SQL (PostgreSQL) instance. | P0 | Pending |
| **REQ-021** | **Portfolio Analytics API**: Implement `GET /investment` to return aggregated portfolio metrics (total value, gain/loss, holdings). | P1 | Pending |
| **REQ-022** | **Transaction CRUD**: Implement `POST`, `GET`, `PUT`, `DELETE` endpoints for user investment transactions at `/investment/transactions`. | P1 | Pending |
| **REQ-023** | **SQLAlchemy Models**: Refactor existing models to support PostgreSQL and ensure proper schema mapping for financial data. | P0 | Pending |

## 4. Documentation & Maintenance

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-030** | **Environment Configuration**: Update `.env` templates to include Google Cloud SQL connection strings and API keys. | P0 | Pending |
| **REQ-031** | **API Documentation**: Ensure all endpoints are documented with proper request/response schemas in the codebase. | P1 | Pending |
| **REQ-032** | **Testing Suite**: Update pytest to cover FastAPI endpoints and integration with the cloud database. | P1 | Pending |

## Success Criteria

1.  A user can send a chat message via the `/chat` API and receive a streaming response in real-time.
2.  Chat history and agent state are preserved across requests via `thread_id`.
3.  Investments and transactions are persisted to Google Cloud SQL and accessible via REST endpoints.
4.  The application passes all integration tests for the new API-first architecture.
