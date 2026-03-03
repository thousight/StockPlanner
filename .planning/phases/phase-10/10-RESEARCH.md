# Phase 10: JWT Authentication - Research

**Researched:** 2025-03-05
**Domain:** Authentication, JWT, Session Management, SQLAlchemy
**Confidence:** HIGH

## Summary

This research establishes the implementation strategy for JWT-based authentication in StockPlanner, focusing on secure session management through **Refresh Token Rotation** and **Theft Detection**. 

The core approach uses `PyJWT` for stateless access tokens and a stateful `RefreshToken` table in PostgreSQL to manage sessions. To ensure high security with minimal friction, we implement a 10-second grace period for rotated tokens, allowing legitimate concurrent requests (e.g., from multiple mobile tabs) to succeed while aggressively revoking all sessions if a token is reused outside this window.

**Primary recommendation:** Use `PyJWT` for token operations and implement a stateful refresh flow in the `auth` service that handles rotation, grace periods, and user-wide revocation on theft detection.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Access Token TTL:** 10 minutes.
- **Refresh Token TTL:** 10 minutes.
- **Expiration Response:** Return `401 Unauthorized` when a token expires, signaling the client to initiate the refresh flow.
- **Persistence:** Lifetimes are fixed; no "Remember Me" logic for this phase.
- **Theft Detection:** If a previously used (rotated) refresh token is presented, **invalidate all active sessions** for that user immediately.
- **Session Limits:** Unlimited simultaneous sessions allowed per user.
- **Sign-Out:** `POST /auth/signout` invalidates only the specific refresh token used in the request.
- **Metadata:** Store the `User-Agent` alongside refresh tokens in the database for session tracking and auditing.
- **Security Hardening:** Provide a `POST /auth/revoke-all` endpoint to invalidate all sessions for the current user.
- **Sign-In Response:** Return only the token pair (`access_token`, `refresh_token`) and `token_type`. Do not include user profile data.
- **Error Privacy:** Use a single generic error message ("Invalid email or password") for all authentication failures to prevent user enumeration.
- **Race Condition Handling:** Implement a **10-second grace period** for refresh tokens after they have been rotated to accommodate concurrent mobile requests or network latency.
- **Auth Dependency:** Create a `get_current_user` FastAPI dependency that verifies the JWT and ensures the user status is `ACTIVE`.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | Implement Sign-In API | Sign-in logic with Argon2id and JWT generation is detailed in [Code Examples](#sign-in-logic). |
| AUTH-02 | JWT Generation (Access + Refresh) | Payload structure and TTLs are defined in [JWT Payload Structure](#jwt-payload-structure). |
| AUTH-03 | Refresh Token Rotation | Rotation logic with `parent_token_id` is detailed in [Architecture Patterns](#pattern-1-refresh-token-rotation). |
| AUTH-04 | Theft Detection | Logic to revoke all sessions on reuse is detailed in [Common Pitfalls](#pitfall-1-token-reuse--theft-detection). |
| AUTH-05 | Auth Middleware | `get_current_user` logic with ACTIVE check is defined in [Code Examples](#get_current_user-dependency). |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyJWT | 2.10.1+ | JWT Signing & Verification | Most modern, secure, and actively maintained JWT library for Python. Recommended over `python-jose`. |
| argon2-cffi | 23.1.0+ | Password Hashing | Industry standard (Argon2id) for password security (already in project). |
| cryptography | 43.0.0+ | Backend for PyJWT | Provides secure cryptographic primitives. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| hashlib | (Stdlib) | Token Hashing | Used to generate `token_hash` from JWT `jti` (SHA-256). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyJWT | python-jose | `python-jose` is effectively unmaintained and has known unpatched vulnerabilities (e.g., CVE-2024-33664). |
| Opaque Tokens | JWT for Refresh | Opaque tokens are simpler but require DB lookup for *every* attribute. JWTs allow metadata to be encoded, though we still do DB lookup for rotation/revocation. |

**Installation:**
```bash
pip install pyjwt[crypto]
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── controllers/
│   └── auth.py         # Sign-in, Sign-out, Refresh, Revoke-all endpoints
├── services/
│   └── auth.py         # JWT creation, rotation logic, theft detection
├── database/
│   └── models.py       # RefreshToken model
└── schemas/
    └── auth.py         # TokenResponse, SignInRequest
```

### Pattern 1: Refresh Token Rotation
**What:** Every time a refresh token is used, it is revoked and a new one is issued.
**When to use:** All session-based applications to prevent persistent session theft.
**Example (SQLAlchemy 2.0):**
```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid7.uuid7()))
    token_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    user_agent = Column(String, nullable=True)
    parent_token_id = Column(String, ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True)
    rotated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
```

### Anti-Patterns to Avoid
- **Infinite Refresh Tokens:** Never allow a refresh token to be used indefinitely. Rotation + Short TTL (10 min) is key.
- **Storing Raw Tokens:** Never store the raw JWT or secret string in the DB. Store a SHA-256 hash of the `jti` or the token itself.
- **Broad Error Messages:** Don't tell the user "User not found" or "Password incorrect". Use "Invalid email or password".

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JWT Signature | Custom HMAC | PyJWT | Complex edge cases in padding and algorithm confusion. |
| UUID Generation | string manipulation | uuid-utils / uuid7 | Ensures high entropy and sortable IDs (UUIDv7). |
| Date Math | manual seconds | datetime + timedelta | Handles leap seconds and timezone offsets correctly. |

## Common Pitfalls

### Pitfall 1: Token Reuse & Theft Detection
**What goes wrong:** A stolen refresh token is used by an attacker. The legitimate user's client might also try to use it.
**Why it happens:** In basic rotation, the first use revokes the token. If used again, it's either an attacker or a race condition.
**How to avoid:** 
1. Check `rotated_at`.
2. If set and `now - rotated_at > 10s`, assume theft.
3. Perform a mass revocation: `DELETE FROM refresh_tokens WHERE user_id = :user_id`.

### Pitfall 2: Race Conditions (Multi-tab)
**What goes wrong:** User has 3 tabs open. All 3 try to refresh at once. Tab 1 succeeds; Tab 2 and 3 fail and log the user out.
**How to avoid:** The **10-second grace period**. If `rotated_at` is set but within the window, allow the refresh to proceed as if valid (or return the child token if stored).

## JWT Payload Structure

### Access Token
```json
{
  "sub": "user_uuid",       // Subject (User ID)
  "iat": 1710000000,        // Issued At
  "exp": 1710000600,        // Expiration (iat + 600s)
  "jti": "random_uuid",     // Unique identifier for revocation check
  "type": "access"          // Token type discriminator
}
```

### Refresh Token
```json
{
  "sub": "user_uuid",
  "iat": 1710000000,
  "exp": 1710000600,
  "jti": "random_uuid",
  "type": "refresh"
}
```

## Code Examples

### get_current_user Dependency
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        user = await db.get(User, user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="User inactive or not found")
            
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Refresh Logic with Grace Period
```python
async def refresh_session(db: AsyncSession, refresh_token: str, user_agent: str):
    # 1. Decode & Verify JWT
    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    jti_hash = hashlib.sha256(payload["jti"].encode()).hexdigest()
    
    # 2. Lookup DB Record
    stmt = select(RefreshToken).where(RefreshToken.token_hash == jti_hash)
    token_record = (await db.execute(stmt)).scalar_one_or_none()
    
    if not token_record or token_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 3. Handle Rotation & Theft Detection
    if token_record.rotated_at:
        age = datetime.now(timezone.utc) - token_record.rotated_at
        if age > timedelta(seconds=10):
            # THEFT DETECTED: Revoke everything
            await db.execute(delete(RefreshToken).where(RefreshToken.user_id == token_record.user_id))
            await db.commit()
            raise HTTPException(status_code=401, detail="Security breach detected. Sessions invalidated.")
        else:
            # Grace period: Proceed with issuing a new token, but maybe reuse family logic
            pass

    # 4. Perform Rotation
    # ... mark old as rotated, create new access/refresh pair ...
```

## Open Questions

1. **Mass Revocation Method:** Should we `DELETE` or `UPDATE expires_at = now`?
   - *Recommendation:* `DELETE` is cleaner and ensures database size remains manageable. If audit logs are needed, a separate `AuditLog` table is better than keeping expired tokens.
2. **Grace Period Return Value:** If a tab refreshes within the grace period, should it get a *new* token pair or the *exact same* pair as the first refresh?
   - *Recommendation:* Generating a new pair is simpler to implement and safe within the 10s window.

## Sources

### Primary (HIGH confidence)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/) - Verification of current API and security best practices.
- [FastAPI Security Docs](https://fastapi.tiangolo.com/tutorial/security/) - Verification of dependency injection patterns.
- [Auth0: Refresh Token Rotation](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation) - Standard pattern for rotation and theft detection.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PyJWT is the industry standard for Python.
- Architecture: HIGH - Rotation + Grace Period is a well-documented security pattern.
- Pitfalls: HIGH - Theft detection logic follows Auth0 recommendations.

**Research date:** 2025-03-05
**Valid until:** 2025-04-05
