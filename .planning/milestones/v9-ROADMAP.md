# Roadmap - Milestone 9: OAuth & Google Sign-In

This roadmap outlines the phases for implementing OAuth with Google Identity Services for unified authentication.

## Phase 37: Google Identity Handshake
**Goal:** Implement the backend endpoint to validate Google ID tokens.
- [ ] Integration of `google-auth` library for token verification.
- [ ] User lookup and profile creation from Google data (Email, Name, Avatar).
- [ ] Secure JWT issuance for social-login sessions.

## Phase 38: Account Linking Strategy
**Goal:** Merge existing email users with social login accounts.
- [ ] Implementation of the `Account Link` logic (Prompting or auto-linking).
- [ ] Database updates to support multiple identity providers per user.
- [ ] Handling of email collisions and security prompts.

## Phase 39: Flutter Integration Prep
**Goal:** Finalize the API for mobile client compatibility.
- [ ] Ensuring redirect URIs work for mobile deep links.
- [ ] Implementation of mobile-specific token refresh flows for social login.
- [ ] Validation of scopes for mobile analytics (optional).

## Phase 40: Security Audit & Cleanup
**Goal:** Finalize security measures and documentation.
- [ ] External audit of JWT claims and provider isolation.
- [ ] Final documentation for mobile team integration.
- [ ] Stress testing the authentication flow.
