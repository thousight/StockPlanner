# Context - Phase 9: User Foundation

This document captures implementation decisions for the User database foundation and initial registration flow.

## 1. Profile Scope & Schema
- **Mandatory Fields (at Sign-Up):**
    - Email (Unique index).
    - Password (to be hashed with Argon2id).
    - First Name.
    - Last Name.
    - Risk Tolerance (Enum or range).
    - Base Currency (e.g., USD, EUR).
- **Optional Fields:**
    - Middle Name.
    - Date of Birth (Used for risk profiling).
    - Display Name.
    - Avatar URL.
    - Bio.
- **Audit Fields:**
    - `created_at`, `updated_at`, `last_login_at`.

## 2. Registration & Validation UX
- **Email Validation:** Standard format check; return a specific "Email already in use" error if a conflict occurs.
- **Password Complexity:** Minimum 8 characters, must include special characters.
- **Activation Flow:** New users are created in a **Pending/Inactive** state. An email verification step is required before the account becomes **Active**.
- **Sign-Up Response:** `POST /auth/signup` will return a `201 Created` status only (no tokens issued yet), directing the user to verify their email.
- **Sign-In Response:** `POST /auth/signin` will return the JWT Access + Refresh token pair upon successful authentication of an Active account.

## 3. Account Lifecycle
- **Deletion Strategy:** **Soft Delete** only.
- **Data Retention:** Retain user data for **6 months** after soft deletion before permanent scrubbing.
- **Client Metadata:** Tracking the client type (e.g., Flutter vs Web) is **not required** for this phase.
