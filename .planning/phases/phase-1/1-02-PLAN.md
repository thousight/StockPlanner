---
phase: phase-1
plan: 1-02
type: execute
wave: 2
depends_on: [1-01]
files_modified: [src/config.py, src/middleware.py, src/main.py]
autonomous: true
requirements: [REQ-001, REQ-002]
user_setup: []

must_haves:
  truths:
    - "FastAPI server starts without errors"
    - "X-Request-ID is present in response headers"
    - "Swagger UI is accessible at /swagger"
  artifacts:
    - path: "src/config.py"
      provides: "Type-safe settings management via Pydantic"
    - path: "src/middleware.py"
      provides: "Correlation ID and exclude_none route class"
    - path: "src/main.py"
      provides: "Application entry point and lifespan management"
  key_links:
    - from: "src/main.py"
      to: "src/middleware.py"
      via: "route_class override"
      pattern: "app\.router\.route_class = ExcludeNoneRoute"
---

<objective>
Setup core FastAPI application with standardized middleware, configuration, and lifespan management.

Purpose: Establish the runtime environment for the API with proper request tracking and response formatting.
Output: Working FastAPI application skeleton.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phase-1/1-CONTEXT.md
@.planning/phase-1/1-RESEARCH.md
@.planning/phase-1/phase-1-1-01-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Configuration & Middleware</name>
  <files>src/config.py, src/middleware.py</files>
  <action>
    1. Create `src/config.py`:
       - Use `pydantic_settings.BaseSettings`.
       - Define settings for `database_url`, `environment`, `port`, `log_level`, etc.
       - Use `model_config = SettingsConfigDict(env_file=".env")`.
    2. Create `src/middleware.py`:
       - Implement `ExcludeNoneRoute` class (inheriting from `APIRoute`) that sets `response_model_exclude_none=True` by default.
       - Refer to Pattern 1 in `1-RESEARCH.md`.
  </action>
  <verify>Check `src/config.py` for correct Pydantic settings and `src/middleware.py` for the route class implementation.</verify>
  <done>Core configuration and middleware components are implemented.</done>
</task>

<task type="auto">
  <name>Task 2: Main Application & Lifespan</name>
  <files>src/main.py</files>
  <action>
    1. Create `src/main.py`:
       - Initialize `FastAPI` with `docs_url="/swagger"`.
       - Set `app.router.route_class = ExcludeNoneRoute`.
       - Add `CorrelationIdMiddleware` from `asgi-correlation-id` for `X-Request-ID`.
       - Setup `CORSMiddleware` allowing all origins (`*`) for MVP.
       - Implement `lifespan` context manager for future database engine management (currently just a placeholder with logging).
       - Include a basic root endpoint returning `{"status": "ok"}`.
  </action>
  <verify>Run the server locally with `uvicorn src.main:app` and check `curl -I http://localhost:8000/` for the `X-Request-ID` header.</verify>
  <done>FastAPI application is initialized and running with required middleware.</done>
</task>

</tasks>

<verification>
Run `curl http://localhost:8000/swagger` to verify docs are served. Verify that a sample response with a null field actually omits that field.
</verification>

<success_criteria>
- FastAPI app starts and responds to root endpoint.
- `X-Request-ID` is present in all response headers.
- Response JSONs omit `null` fields globally.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-1/phase-1-1-02-SUMMARY.md`
</output>
