# Requirements - Milestone 2: Basic Authentication & User Management

This milestone establishes a complete, secure authentication flow for the StockPlanner API, enabling multi-user support and data isolation.

## 1. User Management & Security

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-040** | **Secure Password Hashing**: Use Argon2id (`argon2-cffi`) for storing user passwords with recommended salt/memory parameters. | P0 | Pending |
| **REQ-041** | **User Model (UUIDv7)**: Implement a User model with sortable UUIDv7 primary keys, storing email (unique), hashed password, full name, and audit timestamps. | P0 | Pending |
| **REQ-042** | **Sign-Up API**: Create `POST /auth/signup` to register new users with standard profiles. | P0 | Pending |
| **REQ-043** | **Sign-In API**: Create `POST /auth/signin` to authenticate users and issue Access + Refresh tokens. | P0 | Pending |

## 2. JWT & Session Management

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-050** | **Access Token Flow**: Implement short-lived JWT access tokens using `PyJWT` for all protected endpoints. | P0 | Pending |
| **REQ-051** | **Refresh Token Rotation**: Implement database-stored refresh tokens with rotation (issuing a new refresh token on every use) to detect and prevent token theft. | P1 | Pending |
| **REQ-052** | **Token Refresh API**: Create `POST /auth/refresh` to exchange a valid refresh token for a new pair of tokens. | P1 | Pending |
| **REQ-053** | **Sign-Out API**: Create `POST /auth/signout` to invalidate the current refresh token session. | P1 | Pending |

## 3. Authorization & Isolation

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-060** | **Auth Middleware/Dependency**: Implement a FastAPI dependency (`get_current_user`) to verify JWTs and inject the user object into route handlers. | P0 | Pending |
| **REQ-061** | **Data Isolation (API Layer)**: Refactor all existing financial and chat endpoints to filter data strictly by the authenticated `user_id`. | P0 | Pending |
| **REQ-062** | **Thread Ownership**: Ensure chat threads and agent interactions are strictly owned by the user who created them. | P0 | Pending |

## Success Criteria

1.  A user can register, log in, and receive valid Access and Refresh tokens.
2.  All previously public endpoints (Portfolio, Transactions, Chat) now require a valid `Authorization: Bearer <token>` header.
3.  Users cannot access or modify data belonging to other users.
4.  Invalid or expired tokens result in a 401 Unauthorized response.
5.  Database-level isolation is verified via integration tests.
