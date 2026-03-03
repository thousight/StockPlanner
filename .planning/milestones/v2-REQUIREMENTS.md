# Requirements Archive - Milestone 2: Basic Authentication & User Management

This document records the final status of requirements for Milestone 2.

## Status Summary
- **Total Requirements:** 11
- **Completed:** 11
- **Deferred:** 0
- **Status:** 100% Complete

## 1. User Management & Security

| ID | Requirement | Status | Outcome |
|---|---|---|---|
| **REQ-040** | Secure Password Hashing | DONE | Implemented with Argon2id via `argon2-cffi`. |
| **REQ-041** | User Model (UUIDv7) | DONE | Created `User` table with UUIDv7 primary keys. |
| **REQ-042** | Sign-Up API | DONE | `POST /auth/signup` implemented with strict validation. |
| **REQ-043** | Sign-In API | DONE | `POST /auth/signin` implemented with OAuth2 form support. |

## 2. JWT & Session Management

| ID | Requirement | Status | Outcome |
|---|---|---|---|
| **REQ-050** | Access Token Flow | DONE | 10m JWT access tokens implemented. |
| **REQ-051** | Refresh Token Rotation | DONE | Security rotation with 10s grace period functional. |
| **REQ-052** | Token Refresh API | DONE | `POST /auth/refresh` exchanges rotated tokens. |
| **REQ-053** | Sign-Out API | DONE | `POST /auth/signout` invalidates specific refresh tokens. |

## 3. Authorization & Isolation

| ID | Requirement | Status | Outcome |
|---|---|---|---|
| **REQ-060** | Auth Middleware/Dependency | DONE | `set_user_context` dependency enforces JWT validation. |
| **REQ-061** | Data Isolation (API Layer) | DONE | All endpoints filter data by JWT `sub` claim. |
| **REQ-062** | Thread Ownership | DONE | Strict 1:1 ownership for chat threads verified. |

## Success Criteria Verification
1. [x] A user can register, log in, and receive valid Access and Refresh tokens.
2. [x] All previously public endpoints (Portfolio, Transactions, Chat) now require a valid `Authorization: Bearer <token>` header.
3. [x] Users cannot access or modify data belonging to other users.
4. [x] Invalid or expired tokens result in a 401 Unauthorized response.
5. [x] Database-level isolation is verified via integration tests.
