# Phase 1: API Scaffolding - Research

**Researched:** 2026-02-28
**Domain:** FastAPI, Async Architecture, Railway Deployment
**Confidence:** HIGH

## Summary

Phase 1 focuses on establishing a production-ready FastAPI foundation. Research confirms that for 2025, the "standard" approach for async Python services involves SQLAlchemy 2.0 with `asyncpg`, `asgi-correlation-id` for request tracking, and a robust `lifespan` pattern for resource management. Deployment to Railway requires specific configuration for networking (internal URLs) and environment-aware port binding.

**Primary recommendation:** Use `asgi-correlation-id` to satisfy the `X-Request-ID` requirement and override the FastAPI `route_class` to globally enforce `exclude_none=True` as requested for the Flutter client.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Framework:** FastAPI with asynchronous execution (`async`/`await`).
- **Deployment:** Railway (automatic GitHub deployment to `main` branch).
- **Versioning:** No explicit versioning (e.g., `/v1`).
- **Documentation:** Swagger/OpenAPI available at `/swagger`.
- **Non-Chat APIs:** Return JSON objects directly, omit `null` fields.
- **Error Responses:** Standard FastAPI `{"detail": "message"}` structure.
- **Request Identification:** `X-Request-ID` in response headers.
- **CORS:** Initial setup allow `*`.
- **Database:** SQLAlchemy refactored for PostgreSQL, `create_all()` on startup.

### Claude's Discretion

- Project folder structure and organization.
- Specific libraries for health checks and request tracking.
- Logging configuration details.
- Internal async session management patterns.

### Deferred Ideas (OUT OF SCOPE)

- Explicit API versioning (v1, v2).
- Custom internal error codes.
- Tightened CORS (deferred to Milestone 2).
  </user_constraints>

<phase_requirements>

## Phase Requirements

| ID      | Description                      | Research Support                                                                |
| ------- | -------------------------------- | ------------------------------------------------------------------------------- |
| REQ-001 | FastAPI Framework Implementation | Established best-practice project structure and initialization patterns.        |
| REQ-002 | Asynchronous Architecture        | Verified `asyncpg` + `AsyncSession` as the standard for non-blocking DB access. |
| REQ-003 | Health & Diagnostics             | Documented custom `/health` pattern with DB connectivity checks.                |

</phase_requirements>

## Standard Stack

### Core

| Library             | Version  | Purpose           | Why Standard                                         |
| ------------------- | -------- | ----------------- | ---------------------------------------------------- |
| `fastapi`           | ^0.115.0 | Web Framework     | Industry standard for async Python APIs.             |
| `uvicorn`           | ^0.30.0  | ASGI Server       | High-performance production server.                  |
| `sqlalchemy`        | ^2.0.0   | ORM               | Best-in-class ORM with full async support in 2.0.    |
| `asyncpg`           | ^0.30.0  | DB Driver         | Fastest PostgreSQL driver for async Python.          |
| `pydantic-settings` | ^2.0.0   | Config Management | Modern standard for type-safe environment variables. |

### Supporting

| Library               | Version | Purpose           | When to Use                                |
| --------------------- | ------- | ----------------- | ------------------------------------------ |
| `asgi-correlation-id` | ^4.3.0  | Request Tracking  | Mandatory for `X-Request-ID` requirement.  |
| `python-dotenv`       | ^1.0.0  | Env Loading       | For local development parity with Railway. |
| `httpx`               | ^0.27.0 | Async HTTP Client | For internal service calls or testing.     |

### Alternatives Considered

| Instead of    | Could Use        | Tradeoff                                                          |
| ------------- | ---------------- | ----------------------------------------------------------------- |
| Custom Health | `fastapi-health` | Library adds dependency for a simple 10-line feature.             |
| `psycopg2`    | `asyncpg`        | `psycopg2` is synchronous and blocks the event loop.              |
| `pip`         | `uv`             | `uv` is faster but requires specific Railway build configuration. |

**Installation:**

```bash
pip install fastapi uvicorn[standard] sqlalchemy asyncpg pydantic-settings asgi-correlation-id python-dotenv
```

## Architecture Patterns

### Recommended Project Structure

```
src/
├── api/             # Route handlers
│   ├── routes/      # Logical route groups
│   └── deps.py      # FastAPI Dependencies (get_db, etc.)
├── core/            # Config, Constants, Middleware
│   ├── config.py    # Pydantic Settings
│   └── middleware.py # Custom Route classes/Middleware
├── db/              # Database session & engine
│   └── session.py   # Async engine/sessionmaker
├── models/          # SQLAlchemy Models
├── schemas/         # Pydantic Schemas
└── main.py          # App initialization & Lifespan
```

### Pattern 1: Global `exclude_none` via `route_class`

To ensure all responses omit `null` values for Flutter (as per CONTEXT.md), we override the default route class.

```python
# src/core/middleware.py
from typing import Any, Callable
from fastapi.routing import APIRoute

class ExcludeNoneRoute(APIRoute):
    def __init__(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
        if "response_model_exclude_none" not in kwargs:
            kwargs["response_model_exclude_none"] = True
        super().__init__(path, endpoint, **kwargs)
```

### Pattern 2: Unified Lifespan

Use the `lifespan` context manager to manage engine disposal and initial table creation.

```python
# src/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables (MVP requirement)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Clean up pool
    await engine.dispose()
```

## Don't Hand-Roll

| Problem        | Don't Build       | Use Instead           | Why                                                        |
| -------------- | ----------------- | --------------------- | ---------------------------------------------------------- |
| Request IDs    | Manual Middleware | `asgi-correlation-id` | Handles `contextvars` propagation correctly for async.     |
| DB Pooling     | Custom Pooler     | `SQLAlchemy` Engine   | Built-in pooling is battle-tested and highly configurable. |
| Env Validation | `os.environ.get`  | `pydantic-settings`   | Provides type-safety and fail-fast startup.                |

## Common Pitfalls

### Pitfall 1: Blocking the Event Loop

**What goes wrong:** Using synchronous DB calls (`psycopg2`) or long-running CPU tasks in an `async def` route.
**How to avoid:** Always use `asyncpg` and `await` for I/O. For heavy CPU, use `run_in_executor`.

### Pitfall 2: Railway Port Binding

**What goes wrong:** Hardcoding port `8000` in the start command.
**How to avoid:** Use `uvicorn main:app --host 0.0.0.0 --port $PORT`. Railway injects `$PORT` dynamically.

### Pitfall 3: Public vs Internal DB URLs

**What goes wrong:** Using the public Railway DB URL in the deployed app, causing high latency.
**How to avoid:** Use the internal network URL (e.g., `...railway.internal:5432`) for the backend-to-DB connection.

### Pitfall 4: `expire_on_commit`

**What goes wrong:** Accessing model attributes after a commit throws `Greenlet` or "Missing session" errors.
**How to avoid:** Set `expire_on_commit=False` in `async_sessionmaker`.

## Code Examples

### Request ID & Global Exclude Setup

```python
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware
from src.core.middleware import ExcludeNoneRoute

app = FastAPI(docs_url="/swagger")
app.router.route_class = ExcludeNoneRoute

app.add_middleware(
    CorrelationIdMiddleware,
    header_name='X-Request-ID',
    update_request_header=True
)
```

### Async Database Dependency

```python
# src/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## State of the Art

| Old Approach              | Current Approach                | When Changed   | Impact                                           |
| ------------------------- | ------------------------------- | -------------- | ------------------------------------------------ |
| `on_event("startup")`     | `lifespan` context manager      | FastAPI 0.93.0 | Better resource cleanup and exception handling.  |
| `dict(exclude_none=True)` | `model_dump(exclude_none=True)` | Pydantic V2    | Performance boost via Rust-backed serialization. |
| `psycopg2`                | `asyncpg`                       | -              | True non-blocking PostgreSQL connectivity.       |

## Open Questions

1. **Wait-for-DB on Startup?**
   - What we know: Railway deployments fail if the app starts before the DB is reachable.
   - Recommendation: Use a simple retry loop or `time.sleep` (wrapped in async) in the lifespan for the first DB connection.

2. **CORS for Railway Previews?**
   - What we know: Railway generates random subdomains for PR previews.
   - Recommendation: Since we decided on `*` for the MVP, this is currently handled but needs monitoring.

## Sources

### Primary (HIGH confidence)

- [FastAPI Official Docs](https://fastapi.tiangolo.com/) - Lifespan and Dependency Injection.
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Async session management.
- [Railway Documentation](https://docs.railway.app/) - Networking and deployment patterns.

### Secondary (MEDIUM confidence)

- [asgi-correlation-id GitHub](https://github.com/snok/asgi-correlation-id) - Setup and logging integration.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Standard 2025 FastAPI/SQLAlchemy stack.
- Architecture: HIGH - Follows modern "lifespan" and "dependency" patterns.
- Pitfalls: HIGH - Common issues well-documented in the Railway ecosystem.

**Research date:** 2026-02-28
**Valid until:** 2026-05-28
