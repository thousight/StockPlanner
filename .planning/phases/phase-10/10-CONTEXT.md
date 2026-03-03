# Context - Phase 10: JWT Authentication

This document captures implementation decisions for JWT-based session management, refresh token rotation, and auth middleware.

## 1. Token Lifetimes & Expiration
- **Access Token TTL:** 10 minutes.
- **Refresh Token TTL:** 10 minutes.
- **Expiration Response:** Return `401 Unauthorized` when a token expires, signaling the client to initiate the refresh flow.
- **Persistence:** Lifetimes are fixed; no "Remember Me" logic for this phase.

## 2. Session Security & Rotation
- **Theft Detection:** If a previously used (rotated) refresh token is presented, **invalidate all active sessions** for that user immediately.
- **Session Limits:** Unlimited simultaneous sessions allowed per user.
- **Sign-Out:** `POST /auth/signout` invalidates only the specific refresh token used in the request.
- **Metadata:** Store the `User-Agent` alongside refresh tokens in the database for session tracking and auditing.
- **Security Hardening:** Provide a `POST /auth/revoke-all` endpoint to invalidate all sessions for the current user.

## 3. Response & Error UX
- **Sign-In Response:** Return only the token pair (`access_token`, `refresh_token`) and `token_type`. Do not include user profile data.
- **Error Privacy:** Use a single generic error message ("Invalid email or password") for all authentication failures to prevent user enumeration.
- **Race Condition Handling:** Implement a **10-second grace period** for refresh tokens after they have been rotated to accommodate concurrent mobile requests or network latency.

## 4. Middleware & Integration
- **Auth Dependency:** Create a `get_current_user` FastAPI dependency that verifies the JWT and ensures the user status is `ACTIVE`.
