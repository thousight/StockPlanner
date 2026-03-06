# Requirements - Milestone 9: OAuth & Google Sign-In

This milestone focuses on expanding authentication options to improve mobile onboarding and security through third-party identity providers.

## 1. Google Identity Integration

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-900** | **Google Identity SDK**: Integration with Google Identity Services for backend token validation. | P0 | [ ] |
| **REQ-901** | **Secure Token Exchange**: Endpoint to exchange Google ID tokens for StockPlanner JWT Access/Refresh tokens. | P0 | [ ] |
| **REQ-902** | **CORS & Redirects**: Proper handling of OAuth redirect URIs and CORS for mobile and web clients. | P1 | [ ] |

## 2. Account Management

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-910** | **Account Linking**: Logic to link an existing email/password account with a Google account (if emails match). | P0 | [ ] |
| **REQ-911** | **Unified User Profile**: Ensure a single User entity in the DB can represent multiple authentication methods. | P0 | [ ] |
| **REQ-912** | **Social Login UI Prep**: API support for returning available login methods for a given user. | P1 | [ ] |

## 3. Security & Validation

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-920** | **JWT Claims Validation**: Verify standard Google claims (aud, iss, exp) and custom scopes. | P0 | [ ] |
| **REQ-921** | **Secure Storage**: Storage of Google provider metadata without exposing internal session keys. | P1 | [ ] |
| **REQ-922** | **Migration Support**: Seamlessly upgrade existing users to social login without data loss. | P1 | [ ] |
