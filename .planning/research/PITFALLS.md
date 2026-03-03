# Domain Pitfalls: Authentication & Security

**Domain:** Financial Services (Mobile-First)
**Researched:** 2025-05-24
**Confidence:** HIGH

## Critical Pitfalls (Security Risks)

### Pitfall 1: JWT Secret Leakage
**What goes wrong:** Using weak or hardcoded secrets for token signing.
**Consequences:** Attackers can forge tokens for any user.
**Prevention:** Use `pydantic-settings` to load secrets from environment variables. Use 32-64 byte random keys (generated via `openssl rand -hex 32`).

### Pitfall 2: Refresh Token Theft
**What goes wrong:** Attackers steal a long-lived refresh token from mobile storage.
**Consequences:** Continuous access even after password change.
**Prevention:** Implement **Refresh Token Rotation** and **Token Families**. Storing the hash in the DB prevents theft from DB leaks.

### Pitfall 3: Replay Attacks
**What goes wrong:** Reusing old JWT tokens after logout.
**Consequences:** Session hijacking.
**Prevention:** Use a short `exp` (5-15 mins). For high-security, implement a **Revocation List (Blacklist)** in Redis for immediate invalidation of the short-lived access token.

## Moderate Pitfalls (Developer Experience/Architecture)

### Pitfall 1: Using `python-jose`
**What goes wrong:** Relying on the stale library mentioned in old tutorials.
**Prevention:** Explicitly use **PyJWT**. The migration is simple and solves multiple unpatched CVEs.

### Pitfall 2: UTC Timestamp Errors
**What goes wrong:** Using `datetime.now()` without timezone info in Python 3.12+.
**Consequences:** Expiration logic failure or logic drift between server/client.
**Prevention:** Use `datetime.now(datetime.UTC)`. Avoid `utcnow()` as it's deprecated.

## Minor Pitfalls

### Pitfall 1: Overly Large JWT Payloads
**What goes wrong:** Including massive role lists or profile data in the token.
**Consequences:** Increased bandwidth on mobile, slower requests.
**Prevention:** Keep JWTs < 500 bytes. Use compact IDs for claims.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Initial Auth | Weak Argon2 parameters | Use `argon2-cffi` defaults (RFC 9106) for standard web apps. |
| Mobile Launch | Insecure Storage | Document requirements for iOS Keychain/Android Keystore. |
| Scaling | DB Refresh Bottleneck | Add index on `token_hash` and consider Redis cache layer. |

## Sources
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Snyk Advisor (Security for Python Libraries)](https://snyk.io/advisor/)
- [Common Vulnerabilities and Exposures (CVE) Database](https://cve.mitre.org/)
