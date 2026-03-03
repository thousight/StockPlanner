# Research Summary: FastAPI Authentication & Security (2025)

**Domain:** Financial Services (Mobile-First)
**Researched:** 2025-05-24
**Overall confidence:** HIGH

## Executive Summary

Authentication for modern financial applications in 2025 has moved beyond simple JWT tokens toward **stateless access tokens** paired with **stateful, rotated refresh tokens**. The industry consensus has shifted toward **PyJWT** for JWT handling (replacing the unmaintained `python-jose`) and **Argon2id** (via `argon2-cffi`) for GPU-resistant password hashing.

For mobile-first apps, JWT claims must be minimal to preserve bandwidth, while the backend requires robust **Refresh Token Rotation** and **Token Family Tracking** to detect and mitigate token theft immediately. A hybrid storage strategy (PostgreSQL for persistence and audit, Redis for performance/blacklisting) is the recommended path for scalability.

The user profile schema should be built with **Zero Trust** principles, using **UUIDv7** for non-enumerable, sortable identifiers and **Field-Level Encryption** for PII (GDPR/SOC2 compliance).

## Key Findings

**Stack:** FastAPI + PyJWT (v2.8+) + argon2-cffi + PostgreSQL (refresh tokens).
**Architecture:** Secure Hybrid JWT with Refresh Token Rotation and Token Families.
**Critical Pitfall:** Avoid `python-jose` and `passlib`; use modern maintained alternatives to prevent CVE exposure.

## Implications for Roadmap

Based on research, suggested phase structure for Authentication:

1. **Security Foundation (Phase 1)** - Establishment of hashing & core schema.
   - Addresses: Argon2id Hashing, User Profile Schema with UUIDv7.
   - Avoids: Weak hashing algorithms and enumerable integer IDs.

2. **Core Auth Flow (Phase 2)** - Implementation of the JWT lifecycle.
   - Addresses: Login, Access JWT (5-15m), Database-backed Refresh Tokens.
   - Avoids: Storing raw refresh tokens in the DB (store hashes instead).

3. **Advanced Security (Phase 3)** - Hardening for production/compliance.
   - Addresses: Refresh Token Rotation, Token Family tracking, and MFA state.
   - Avoids: Long-lived access windows and session hijacking.

**Phase ordering rationale:**
- Foundation must be solid (Argon2 + UUIDs) before tokens are issued.
- Refresh Token storage in DB is the MVP; Redis can be added later for scale.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Clear industry consensus for 2024/2025. |
| Features | HIGH | Based on OWASP and NIST security standards. |
| Architecture | HIGH | Proven patterns for secure session management. |
| Pitfalls | HIGH | Validated against recent CVEs and maintenance statuses. |

## Gaps to Address

- **Field-Level Encryption (FLE):** Implementation details for specific KMS providers (AWS KMS vs HashiCorp Vault) depend on infra choice.
- **Biometric Integration:** Mobile-side research required for deep integration with iOS/Android hardware keys.
- **MFA Methods:** Decisions on SMS vs TOTP vs Passkeys should be finalized during the design phase.
