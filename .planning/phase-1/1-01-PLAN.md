---
phase: phase-1
plan: 1-01
type: execute
wave: 1
depends_on: []
files_modified: [requirements.txt, src/core/config.py, src/db/session.py, src/models/base.py, src/core/middleware.py, src/main.py, src/api/deps.py, src/api/routes/health.py]
autonomous: true
requirements: [REQ-001, REQ-002, REQ-003]
user_setup:
  - service: Railway PostgreSQL
    why: "Required for async database connectivity and health checks"
    env_vars:
      - name: DATABASE_URL
        source: "Railway Project -> PostgreSQL -> Variables -> DATABASE_PRIVATE_URL (or local postgres for dev)"
must_haves:
  truths:
    - "The server starts without errors using uvicorn"
    - "GET /swagger returns the OpenAPI documentation"
    - "GET /health returns a JSON response with status 'ok'"
    - "API responses include an X-Request-ID header"
    - "JSON responses omit fields with null values"
  artifacts:
    - path: "src/main.py"
      provides: "FastAPI application instance with lifespan and middleware"
    - path: "src/db/session.py"
      provides: "Async SQLAlchemy engine and sessionmaker"
    - path: "src/core/middleware.py"
      provides: "Global null-field exclusion logic"
    - path: "src/api/routes/health.py"
      provides: "Service health monitoring endpoint"
  key_links:
    - from: "src/main.py"
      to: "src/db/session.py"
      via: "lifespan context manager"
      pattern: "engine.dispose"
    - from: "src/main.py"
      to: "asgi_correlation_id"
      via: "middleware registration"
      pattern: "CorrelationIdMiddleware"
---

<objective>
Establish a production-ready FastAPI foundation for the StockPlanner backend, implementing async architecture, request tracking, and health monitoring.

Purpose: Provides the scaffolding required for Railway deployment and future agentic features.
Output: A functional FastAPI server with async DB connectivity and standardized response behavior.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/phase-1/1-CONTEXT.md
@.planning/phase-1/1-RESEARCH.md
@.planning/STATE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Core Configuration and Async Database Setup</name>
  <files>requirements.txt, src/core/config.py, src/db/session.py, src/models/base.py</files>
  <action>
    1. Update `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0.0`, `asyncpg`, `pydantic-settings`, `asgi-correlation-id`, `python-dotenv`.
    2. Create `src/core/config.py` using `pydantic_settings.BaseSettings` to manage `DATABASE_URL` and `ENV`. Load from `.env` if present.
    3. Create `src/db/session.py` implementing `create_async_engine` and `async_sessionmaker(expire_on_commit=False)`.
    4. Create `src/models/base.py` defining a standard `DeclarativeBase` for the project.
    
    Avoid using synchronous `psycopg2` as it will block the event loop; ensure `DATABASE_URL` uses the `postgresql+asyncpg://` scheme.
  </action>
  <verify>Run `pip install -r requirements.txt` and verify `DATABASE_URL` is parsed correctly by a temporary script importing `Settings`.</verify>
  <done>Async database infrastructure and type-safe configuration are available for the application.</done>
</task>

<task type="auto">
  <name>Task 2: FastAPI Application and Global Middleware</name>
  <files>src/core/middleware.py, src/main.py, src/api/deps.py</files>
  <action>
    1. Create `src/core/middleware.py` implementing `ExcludeNoneRoute(APIRoute)` which sets `response_model_exclude_none = True` by default to satisfy Flutter client requirements.
    2. Create `src/main.py` with:
       - `FastAPI(docs_url="/swagger")`.
       - `app.router.route_class = ExcludeNoneRoute`.
       - `CorrelationIdMiddleware` registered with `header_name='X-Request-ID'`.
       - `CORSMiddleware` allowing all origins (`*`) for MVP development.
       - A `lifespan` context manager that handles `engine.dispose()` on shutdown.
    3. Create `src/api/deps.py` with an async `get_db` dependency yielding a session.
    
    Note: For Railway compatibility, ensure the app is prepared to bind to the `$PORT` environment variable if passed via CLI.
  </action>
  <verify>Start the server with `uvicorn src.main:app --reload` and check that `http://localhost:8000/swagger` loads correctly.</verify>
  <done>Application initialized with request tracking, CORS, and optimized JSON serialization.</done>
</task>

<task type="auto">
  <name>Task 3: Health Monitoring and Infrastructure Verification</name>
  <files>src/api/routes/health.py, src/main.py</files>
  <action>
    1. Create `src/api/routes/health.py` with a `GET /health` endpoint.
    2. The endpoint should perform a simple `SELECT 1` query using the `get_db` dependency to verify database connectivity.
    3. Include application status and potentially a timestamp in the response.
    4. Register the health router in `src/main.py`.
  </action>
  <verify>
    1. Call `curl -i http://localhost:8000/health`.
    2. Confirm status is 200 OK.
    3. Confirm `X-Request-ID` is present in headers.
    4. Confirm response body does not contain null fields if any were added.
  </verify>
  <done>Infrastructure is verifiable via /health and monitoring headers are active.</done>
</task>

</tasks>

<verification>
1. Start the server: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
2. Validate Swagger: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/swagger` (Expected: 200)
3. Validate Health: `curl -s http://localhost:8000/health` (Expected: {"status": "ok", ...})
4. Validate Request ID: `curl -I http://localhost:8000/health | grep X-Request-ID` (Expected: header present)
</verification>

<success_criteria>
- FastAPI server is running asynchronously with no blocking calls on the main thread.
- Database connectivity is established and verified via the /health endpoint.
- OpenAPI documentation is accessible at the custom /swagger path.
- All responses adhere to the `exclude_none` and `X-Request-ID` requirements.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-1/phase-1-01-SUMMARY.md`
</output>
