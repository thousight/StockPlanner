# Technology Stack: Authentication & Security

**Project:** StockPlanner
**Researched:** 2025-05-24
**Confidence:** HIGH

## Recommended Stack

### Core Authentication

| Technology       | Version | Purpose          | Why                                                                                              |
| ---------------- | ------- | ---------------- | ------------------------------------------------------------------------------------------------ |
| **FastAPI**      | Latest  | Web Framework    | Native support for dependency injection and OAuth2 flows.                                        |
| **PyJWT**        | Latest  | JWT Handling     | Active maintenance, modern security features (JWE/JWK), and superior to the stale `python-jose`. |
| **argon2-cffi**  | Latest  | Password Hashing | Implementing Argon2id (RFC 9106), the current gold standard for password hashing.                |
| **cryptography** | Latest  | Encryption       | Underlying library for PyJWT and field-level encryption.                                         |

### Database & Storage

| Technology     | Version | Purpose       | Why                                                                                              |
| -------------- | ------- | ------------- | ------------------------------------------------------------------------------------------------ |
| **PostgreSQL** | 16+     | Token Store   | Primary source of truth for refresh tokens, audit logs, and session management. Supports UUIDv7. |
| **Redis**      | 8+      | Session Cache | (Optional/Scale) Fast lookup for active sessions and immediate token blacklisting.               |

### Supporting Libraries

| Library               | Version | Purpose      | When to Use                                                                      |
| --------------------- | ------- | ------------ | -------------------------------------------------------------------------------- |
| **pydantic-settings** | Latest  | Config Mgmt  | Managing secrets (SECRET_KEY) and security parameters via environment variables. |
| **pwdlib**            | Latest  | Auth Wrapper | (Optional) Modern alternative to `passlib` for multi-algorithm support.          |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not                                                                            |
| -------- | ----------- | ----------- | ---------------------------------------------------------------------------------- |
| JWT      | PyJWT       | python-jose | `python-jose` is unmaintained since 2021 and has security vulnerabilities.         |
| Hashing  | argon2-cffi | passlib     | `passlib` is largely unmaintained and has issues with Python 3.12+.                |
| Hashing  | argon2-cffi | bcrypt      | Argon2id provides better resistance against GPU cracking and side-channel attacks. |

---

# Technology Stack: AI Memory & State Persistence

**Project:** StockPlanner
**Researched:** 2025-05-24
**Confidence:** HIGH

## Recommended Stack

### Core AI Framework

| Technology                     | Version | Purpose             | Why                                                         |
| ------------------------------ | ------- | ------------------- | ----------------------------------------------------------- |
| **LangGraph**                  | Latest  | Agent Orchestration | Leading framework for cyclical, stateful agent workflows.   |
| **langgraph-checkpoint-redis** | Latest  | Redis Checkpointer  | High-performance, async-native persistence for graph state. |

### Database & Cache

| Technology      | Version | Purpose               | Why                                                                       |
| --------------- | ------- | --------------------- | ------------------------------------------------------------------------- |
| **Redis Stack** | 8.6+    | Transient State Store | Requires RedisJSON and RediSearch modules for `AsyncRedisSaver`.          |
| **PostgreSQL**  | 16+     | Permanent History     | Relational "Source of Truth" for chat history, audit logs, and analytics. |
| **redis**       | 5.0+    | Redis Client          | Python async client with robust connection pooling.                       |
| **psycopg**     | 3.1+    | Postgres Client       | Modern async client with built-in connection pooling (`psycopg_pool`).    |

### Supporting Libraries

| Library      | Version | Purpose         | When to Use                                                        |
| ------------ | ------- | --------------- | ------------------------------------------------------------------ |
| **pydantic** | 2.0+    | Data Validation | Serializing/deserializing messages between LangGraph and Postgres. |

## Alternatives Considered

| Category     | Recommended                | Alternative      | Why Not                                                                                                                            |
| ------------ | -------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Checkpointer | Redis                      | PostgreSQL       | Redis is faster for transient "brain" state; Postgres is better for long-term history but slower for high-frequency state updates. |
| Checkpointer | langgraph-checkpoint-redis | Manual Redis Ops | Native library handles complex state serialization and "Time Travel" logic out-of-box.                                             |
| Redis Client | redis-py (async)           | aioredis         | `aioredis` was merged into `redis-py` (v4.2+). Use `redis.asyncio`.                                                                |

## Installation

```bash
# LangGraph & Redis Checkpointer
pip install langgraph langgraph-checkpoint-redis redis

# Postgres & Pooling
pip install "psycopg[binary,pool]"
```

## Connection Patterns (Railway)

Railway provides `REDIS_URL` and `DATABASE_URL`. Use these directly in your FastAPI lifespan:

```python
import os
from redis.asyncio import Redis

# Redis Connection (Async)
redis_url = os.getenv("REDIS_URL", "redis://default:password@host:port")
# Note: Railway REDIS_URL includes the password and port automatically.
# Use decode_responses=False for the checkpointer as it handles its own serialization.
client = Redis.from_url(redis_url, decode_responses=False)
```

## Sources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [langgraph-checkpoint-redis GitHub](https://github.com/redis-developer/langgraph-redis)
- [Railway Redis Documentation](https://docs.railway.app/databases/redis)
