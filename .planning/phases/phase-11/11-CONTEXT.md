# Context - Phase 11: Authenticated Isolation

This document captures implementation decisions for enforcing multi-tenancy and isolating user data using JWT context.

## 1. Ownership & Data Boundaries
- **Legacy Migration:** All existing records using "test-user" or other legacy identifiers must be migrated to the primary user UUID: `019cb265-1862-76d0-8ebb-10273b096f66`.
- **Global Resources:**
    - **Assets:** Symbols and sector data are shared globally across all users.
    - **News Cache:** Article summaries are global to reduce LLM costs.
    - **FX Rates:** Currency data remains a public utility service.
- **Strict Isolation:** 
    - **Transactions:** Strictly owned by the user.
    - **Threads:** Strict 1:1 user-to-thread ownership; no sharing supported.

## 2. Enforcement & Error UX
- **Stealth Rejection:** Unauthorized attempts to access a resource (Thread or Transaction) belonging to another user must return **`404 Not Found`** instead of `403 Forbidden`.
- **Thread Integrity:** If a request provides a `thread_id` that belongs to a different user, the API must return a `404`.
- **Zero-State Behavior:** The Portfolio API should return a `200 OK` with an empty result if an authenticated user has not yet added any data.

## 3. Context Flow & Agent Personalization
- **Auth Standard:** Rely exclusively on the JWT `sub` claim. The legacy `X-User-ID` header must be removed from all endpoints.
- **Context Propagation:** Use a background context (e.g., `ContextVar`) to propagate the authenticated `user_id` through the service layers, minimizing explicit argument passing.
- **Agent Personalization:** The LangGraph agents must receive the user's full profile (First Name, Risk Tolerance, Base Currency) to personalize suggestions and reports.
- **Audit Logic:** `last_login_at` is updated only during the initial sign-in flow, not on every token refresh.

## 4. Migration Requirements
- Develop a one-time DB script/migration to update all legacy `user_id` fields to `019cb265-1862-76d0-8ebb-10273b096f66`.
