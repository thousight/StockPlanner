# Context - Phase 1: API Scaffolding

This document captures implementation decisions for Phase 1 of the StockPlanner API Backend to guide downstream research and planning.

## 1. API Architecture & Structure
- **Framework:** FastAPI with asynchronous execution (`async`/`await`).
- **Deployment:** Railway (automatic GitHub deployment to `main` branch).
- **Versioning:** No explicit versioning (e.g., `/v1`) as this is the MVP for a dedicated mobile backend.
- **Documentation:** Swagger/OpenAPI available at `/swagger`.

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
