---
phase: phase-9
plan: 9-03
type: execute
wave: 3
depends_on: [9-02]
must_haves:
  truths:
    - Verification of security utilities is mandatory for Milestone 2.
    - API tests must cover both happy paths and validation failures.
  artifacts:
    - path: tests/unit/services/test_auth.py
      provides: Unit tests for hashing and creation logic.
      min_lines: 40
    - path: tests/api/test_auth.py
      provides: Integration tests for /auth/signup.
      min_lines: 50
  key_links:
    - from: Phase 9
      to: REQ-040
      via: Hashing verification in unit tests.
    - from: Phase 9
      to: REQ-042
      via: API behavioral verification in integration tests.
files_modified:
  - tests/unit/services/test_auth.py
  - tests/api/test_auth.py
autonomous: true
requirements:
  - REQ-040: Secure Password Hashing (Argon2id)
  - REQ-042: Sign-Up API
---

# 9-03: User Management Unit Tests

Verify the security and reliability of the user management system through unit and API tests.

## Tasks

<task id="1">
   <name>Unit Test: Auth Service</name>
   <files>
     - tests/unit/services/test_auth.py
   </files>
   <action>
     - Create `tests/unit/services/test_auth.py`:
       - Test `hash_password` returns different hashes for the same input.
       - Test `verify_password` returns `True` for correct match.
       - Test `verify_password` returns `False` for mismatch.
       - Test `create_user` logic (including `HTTPException(409)` on duplicate).
   </action>
   <verify>
     - `pytest tests/unit/services/test_auth.py` should pass with 100% coverage on new methods.
   </verify>
   <done>
     - [ ] Auth service unit tests implemented and passing.
   </done>
</task>

<task id="2">
   <name>API Test: Sign-Up Endpoint</name>
   <files>
     - tests/api/test_auth.py
   </files>
   <action>
     - Create `tests/api/test_auth.py`:
       - Test `POST /auth/signup` with valid data (201).
       - Test validation errors:
         - Weak password (no special char or too short).
         - Invalid email format.
         - Missing mandatory fields.
       - Test duplicate email registration (409).
   </action>
   <verify>
     - `pytest tests/api/test_auth.py` should pass.
   </verify>
   <done>
     - [ ] Auth API integration tests implemented and passing.
   </done>
</task>

## Success Criteria
- 100% path coverage for `hash_password` and `verify_password`.
- Sign-up API robustly handles validation and conflict edge cases.
- All tests pass in the local environment.
