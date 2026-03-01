# Context - Phase 1: API Scaffolding

This document captures implementation decisions for Phase 1 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Project Structure & Naming

- **Framework:** FastAPI with asynchronous execution (`async`/`await`).
- **Deployment:** Railway (automatic GitHub deployment to `main` branch).
- **Architecture Patterns:**
  - `src/main.py`: Application entry point.
  - `src/config.py`: Settings management (Pydantic `BaseSettings`).
  - `src/middleware.py`: Custom Route classes and middleware.
  - `src/database/`: DB connection clients, sessions (`session.py`), and models (`models.py`).
  - `src/api/controllers/`: Feature-based API routers (renamed from "routes").
  - `src/api/schemas/`: Pydantic models for request/response validation.
  - `src/services/`: Business logic and use-case implementations.
  - `src/graphs/`: LangGraph orchestration, including `agents/`, `tools/`, and `utils/`.
- **Organization:**
  - **Controllers:** Grouped by feature (e.g., `src/api/controllers/investments/`).
  - **Database Structure:** Modular structure for sessions and clients (no `__init__.py`).
  - **Models:** Flat `src/database/models.py` for the initial MVP.
  - **Graphs:** Core agentic logic separated from the API and service layers.

## 2. Standardized Response Payloads

- **Non-Chat APIs:**
  - Return JSON objects directly (no success wrapper).
  - Use standard HTTP status codes (2xx) to indicate successful operations.
  - Fields with missing or `null` data will be omitted from the JSON entirely for cleaner parsing in Flutter.
- **Chat APIs:**
  - Must implement the LangGraph Streaming Server-Sent Events (SSE) schema.
  - Token-level streaming for the final agent synthesis.
- **Error Responses:**
  - Use standard FastAPI `{"detail": "message"}` structure.
  - Map specific application failures to standard HTTP status codes (e.g., 404 for missing stocks, 422 for validation).
  - No custom internal error codes (e.g., `ERR_123`) will be implemented at this stage.

## 3. Debugging & Environment

- **Request Identification:** A `X-Request-ID` will be included in the response headers of all API calls to facilitate debugging between Railway logs and the Flutter client.
- **CORS:** Initial setup will allow `*` (any origin) to support local Flutter development and Railway preview environments, to be tightened in Milestone 2.

## 4. Database Baseline (Railway)

- All SQLAlchemy models must be refactored for PostgreSQL compatibility.
- The API will manage initial table creation automatically on startup using `Base.metadata.create_all()` for the MVP phase.
