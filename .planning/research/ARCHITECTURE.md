# Architecture Patterns: Authentication & Security

**Domain:** Financial Services (Mobile-First)
**Researched:** 2025-05-24
**Confidence:** HIGH

## Recommended Architecture: Secure Hybrid JWT

This architecture balances performance with strict security enforcement for a mobile-first financial app.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **Security Service** | Token generation, hashing, verification | Database, Controllers |
| **Auth Controller** | Login, Refresh, Logout, Profile mgmt | Security Service, Database |
| **User Store (DB)** | Profiles, Hashed Passwords, Refresh Tokens | Auth Controller |
| **KMS** | Master keys for field-level encryption | Security Service (Encryption) |

### Data Flow (Login & Refresh)

1.  **Login:** User submits credentials (Argon2id hashing verification).
2.  **Access JWT:** Issued to mobile client (5-15 min lifespan).
3.  **Refresh Token:** Hashed and stored in **Database** (PostgreSQL) with `family_id` and metadata (IP, Device).
4.  **Refresh Flow:** 
    - Client submits `refresh_token`.
    - Server verifies token in DB.
    - If valid, server generates **new** `access_token` and **new** `refresh_token` (Rotation).
    - If an old/used token is submitted, the **entire family** is invalidated immediately (Breach Detection).

## Patterns to Follow

### Pattern 1: Annotated FastAPI Dependencies
Encapsulate user extraction logic for clean controller signatures.

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from src.security.tokens import verify_access_token
from src.database.models import User

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user_id = verify_access_token(token)
    user = await User.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401)
    return user

# In controllers:
# @router.get("/me")
# async def read_me(current_user: Annotated[User, Depends(get_current_user)]): ...
```

### Pattern 2: Secure User Profile Schema (SQLAlchemy/SQLModel)
Prioritize UUIDv7 for sortability and security.

```python
import uuid_utils  # or uuid6 for v7 support
from datetime import datetime, UTC
from sqlalchemy import UUID, Column, String, Boolean, DateTime, JSON

class User(Base):
    id = Column(UUID, primary_key=True, default=uuid_utils.uuid7)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Argon2id hash
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True) # Encrypt with KMS key
    last_login_at = Column(DateTime(timezone=True))
    security_metadata = Column(JSON) # Store device_id, last_ip, browser_fingerprint
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Database-Stored Raw Tokens
**What:** Storing the raw `refresh_token` in the database.
**Why bad:** If the DB is leaked, the attacker gains full access to all user sessions.
**Instead:** Store only the **hash** of the `refresh_token`.

### Anti-Pattern 2: PII in JWT Claims
**What:** Including email or full names in the JWT payload.
**Why bad:** JWTs are Base64 encoded and can be read by anyone (interceptors, logs).
**Instead:** Only include the `sub` (UUID) and necessary permissions/roles (numeric/compact).

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| Token Verification | Local (CPU) | Local (CPU) | Local (CPU) - Stateless scalability. |
| Token Revocation | DB Query | DB Query (Indexed) | Redis Bloom Filter / Blacklist Cache. |
| Password Hashing | Low latency | High latency (needs more workers) | Dedicated Auth Service with GPU-hardened nodes. |

## Sources
- [RFC 7519 (JSON Web Token)](https://datatracker.ietf.org/doc/html/rfc7519)
- [FastAPI Dependency Injection Docs](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [PostgreSQL Performance Tuning for UUIDv7](https://www.postgresql.org/docs/current/datatype-uuid.html)
