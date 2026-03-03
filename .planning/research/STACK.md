# Technology Stack: Authentication & Security

**Project:** StockPlanner
**Researched:** 2025-05-24
**Confidence:** HIGH

## Recommended Stack

### Core Authentication
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **FastAPI** | Latest | Web Framework | Native support for dependency injection and OAuth2 flows. |
| **PyJWT** | Latest | JWT Handling | Active maintenance, modern security features (JWE/JWK), and superior to the stale `python-jose`. |
| **argon2-cffi** | Latest | Password Hashing | Implementing Argon2id (RFC 9106), the current gold standard for password hashing. |
| **cryptography** | Latest | Encryption | Underlying library for PyJWT and field-level encryption. |

### Database & Storage
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **PostgreSQL** | 16+ | Token Store | Primary source of truth for refresh tokens, audit logs, and session management. Supports UUIDv7. |
| **Redis** | 7+ | Session Cache | (Optional/Scale) Fast lookup for active sessions and immediate token blacklisting. |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pydantic-settings** | Latest | Config Mgmt | Managing secrets (SECRET_KEY) and security parameters via environment variables. |
| **pwdlib** | Latest | Auth Wrapper | (Optional) Modern alternative to `passlib` for multi-algorithm support. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| JWT | PyJWT | python-jose | `python-jose` is unmaintained since 2021 and has security vulnerabilities. |
| Hashing | argon2-cffi | passlib | `passlib` is largely unmaintained and has issues with Python 3.12+. |
| Hashing | argon2-cffi | bcrypt | Argon2id provides better resistance against GPU cracking and side-channel attacks. |

## Installation

```bash
# Core Auth Dependencies
pip install "fastapi[standard]" pyjwt[crypto] argon2-cffi pydantic-settings

# For high-performance UUIDs (UUIDv7)
pip install uuid6
```

## Sources
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Argon2-cffi Documentation](https://argon2-cffi.readthedocs.io/)
- [FastAPI Security Guides (2025)](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
