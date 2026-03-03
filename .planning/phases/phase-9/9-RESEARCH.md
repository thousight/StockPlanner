# Phase 9: User Foundation - Research

**Researched:** 2025-05-20 (Current)
**Domain:** Authentication, User Profiling, Database Foundations
**Confidence:** HIGH

## Summary

This research establishes the technical foundation for the User system in StockPlanner. We will implement a robust User model using **UUIDv7** for primary keys, **Argon2id** for secure password hashing, and a strict **Sign-Up validation** flow. The architecture leverages SQLAlchemy 2.0's modern `Mapped` types and Pydantic V2 for schema validation.

**Primary recommendation:** Use `uuid_utils` for high-performance UUIDv7 generation and `argon2-cffi` for password hashing, with a `PENDING` account status as the default registration state to support future email verification.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Profile Scope & Schema:**
    - Mandatory: Email (Unique), Password (Argon2id), First Name, Last Name, Risk Tolerance (Enum), Base Currency.
    - Optional: Middle Name, DOB, Display Name, Avatar URL, Bio.
    - Audit: `created_at`, `updated_at`, `last_login_at`.
- **Registration & Validation UX:**
    - Email Validation: Standard format check; return specific "Email already in use" error on conflict.
    - Password Complexity: Minimum 8 characters, must include special characters.
    - Activation Flow: New users are created in a **Pending/Inactive** state.
    - Sign-Up Response: `201 Created` status only (no tokens issued).
    - Sign-In Response: `POST /auth/signin` returns JWT Access + Refresh tokens (for Active accounts).
- **Account Lifecycle:**
    - Deletion Strategy: **Soft Delete** only.
    - Data Retention: Retain user data for **6 months** after soft deletion.

### Claude's Discretion
- **UUIDv7 Library:** Choice between `uuid_utils`, `uuid6`, or `python-uuidv7`.
- **Risk Tolerance Values:** Specific Enum values (e.g., CONSERVATIVE, MODERATE, AGGRESSIVE).
- **Service Layer Implementation:** Exact structure for handling conflicts and state transitions.

### Deferred Ideas (OUT OF SCOPE)
- **Client Metadata:** Tracking client types (Flutter vs Web) is not required for this phase.
- **Email Verification Implementation:** The *logic* for sending emails is deferred; only the *status* foundation is implemented now.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `uuid_utils` | ^0.14.0 | UUIDv7 Generation | High-performance (Rust), already in env, supports v7. |
| `argon2-cffi` | ^23.1.0 | Password Hashing | Modern, side-channel resistant, recommended by OWASP. |
| `sqlalchemy` | ^2.0.0 | ORM | Project standard, supports native PostgreSQL UUID. |
| `pydantic` | ^2.0.0 | Validation | Project standard, robust regex and email validation. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|--------------|
| `email-validator` | ^2.1.0 | Email Validation | Required by Pydantic's `EmailStr`. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `uuid_utils` | `uuid6` | `uuid6` is pure Python (slower) but more widely recognized in some circles. |
| `argon2-cffi` | `bcrypt` | `bcrypt` is older and lacks memory-hard resistance against ASIC/GPU attacks compared to Argon2id. |

**Installation:**
```bash
pip install "argon2-cffi" "email-validator" "uuid_utils"
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── database/
│   ├── models.py        # Add User model & RiskTolerance Enum
├── schemas/
│   ├── auth.py          # Add UserSignUp, UserResponse schemas
├── services/
│   ├── auth.py          # Add password hashing & user creation logic
└── controllers/
    ├── auth.py          # Add POST /auth/signup endpoint
```

### Pattern 1: UUIDv7 Primary Keys
**What:** Time-ordered UUIDs for better database index performance.
**When to use:** All primary keys for new entities, especially high-growth tables like Users.
**Example:**
```python
# Source: SQLAlchemy 2.0 Docs / Native PostgreSQL Support
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid_utils
import uuid

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid_utils.uuid7
    )
```

### Anti-Patterns to Avoid
- **Storing Plain-Text Passwords:** Never even log them; use `SecretStr` in Pydantic if necessary.
- **Vague Sign-Up Errors:** "Something went wrong" is bad UX. Specifically catch `UniqueViolation` for emails.
- **Issuing Tokens on Sign-Up:** The context explicitly forbids this until email verification.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password Hashing | Custom salt+hash logic | `argon2.PasswordHasher` | Handles salting, iterations, and constant-time comparison automatically. |
| Email Regex | Complex manual regex | `pydantic.EmailStr` | Follows RFC standards and handles edge cases. |
| UUIDv7 | Time-based random logic | `uuid_utils.uuid7` | Ensuring RFC 9562 compliance is non-trivial. |

## Common Pitfalls

### Pitfall 1: Case-Sensitive Emails
**What goes wrong:** Users sign up with `User@Example.com` and later try to log in with `user@example.com`, failing authentication or creating duplicate accounts.
**How to avoid:** Always `lower()` the email before validation and storage.

### Pitfall 2: Argon2 Memory Usage
**What goes wrong:** High memory settings for Argon2 can lead to DoS if many registration/login requests are processed concurrently.
**How to avoid:** Use default parameters from `argon2-cffi` which are tuned for a balance of security and performance.

### Pitfall 3: Soft Delete Indexing
**What goes wrong:** Unique constraints (like email) fail when a user signs up again after deleting their account if the old record still exists with `deleted_at`.
**How to avoid:** Use a partial unique index in PostgreSQL: `CREATE UNIQUE INDEX ix_users_email_active ON users (email) WHERE (deleted_at IS NULL);`

## Code Examples

### Argon2id Utility
```python
# Source: argon2-cffi documentation
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
```

### Sign-Up Pydantic Schema
```python
# Source: Pydantic V2 Documentation
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserSignUp(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    risk_tolerance: RiskTolerance
    base_currency: str = Field(..., min_length=3, max_length=3)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| UUIDv4 | UUIDv7 | 2024 (RFC 9562) | Better DB performance due to time-ordering. |
| PBKDF2/BCrypt | Argon2id | 2015/2021 | Superior resistance to GPU/ASIC attacks. |
| Pydantic V1 | Pydantic V2 | 2023 | Significant performance boost (Rust core). |

## Open Questions

1. **Foreign Key Migration?**
   - What we know: Existing tables use `String` for `user_id`.
   - What's unclear: Should we migrate existing `user_id` columns to `UUID` type immediately or keep them as `String` for compatibility?
   - Recommendation: Use native `UUID` for the User table and plan a migration for other tables in Phase 9.1 or 10 for consistency.

## Sources

### Primary (HIGH confidence)
- [argon2-cffi docs](https://argon2-cffi.readthedocs.io/) - Password hashing best practices.
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#uuid-data-type) - UUID mapping.
- [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html) - UUIDv7 specification.

### Secondary (MEDIUM confidence)
- FastAPI Community Patterns - Sign-up flows and exception handling.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries are mature and project-aligned.
- Architecture: HIGH - Follows SQLAlchemy 2.0 and Pydantic V2 standards.
- Pitfalls: MEDIUM - Soft delete unique constraints require careful index planning.

**Research date:** 2025-05-20
**Valid until:** 2025-11-20
