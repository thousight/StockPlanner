# Context - Phase 12: Memory Refactor

This document captures implementation decisions for migrating LangGraph state persistence from PostgreSQL to high-speed Redis memory.

## 1. State Persistence & TTL Policy
- **Memory Duration:** 30 minutes.
- **TTL Strategy:** Sliding window; the 30-minute timer is reset upon every new interaction within a thread.
- **Manual Control:** Users will not be provided with an explicit API to clear their short-term memory keys; the TTL policy will handle all purging.
- **Scope:** One global policy applied to all agentic checkpoints.

## 2. Migration & Cleanup Strategy
- **Data Transfer:** No migration of existing Postgres checkpoints is required.
- **Decommissioning:** The legacy Postgres checkpoint tables (`checkpoints`, `checkpoint_writes`, `checkpoint_migrations`) will be purged from the database.
- **Code Removal:** The `AsyncPostgresSaver` integration and associated setup code will be removed entirely to keep the codebase lean.

## 3. Availability & Failure Modes
- **Dependency Strictness:** Redis is a hard requirement for chat functionality.
- **Error Handling:** If the Redis instance is unavailable or a connection fails, the API must return a **503 Service Unavailable** status.
- **Stateless Fallback:** There will be **no fallback** to stateless mode or PostgreSQL; the system requires persistent memory to operate.
- **Resilience:** Implement a **Circuit Breaker** pattern to detect Redis failures early and prevent server resource exhaustion during outages.

## 4. Infrastructure
- **Provider:** Managed Redis Stack on Railway.
- **Client:** `redis.asyncio` for high-performance non-blocking operations.
