---
phase: phase-9
plan: 9-02
type: execute
wave: 2
depends_on: [9-01]
must_haves:
  truths:
    - New users must be created in a PENDING status by default.
    - Password complexity is enforced via regex validation in Pydantic.
  artifacts:
    - path: src/schemas/auth.py
      provides: UserSignUp and UserResponse schemas.
      min_lines: 30
    - path: src/controllers/auth.py
      provides: POST /auth/signup endpoint.
      min_lines: 20
  key_links:
    - from: Phase 9
      to: REQ-042
      via: Sign-Up API implementation.
files_modified:
  - src/schemas/auth.py
  - src/services/auth.py
  - src/controllers/auth.py
  - main.py
autonomous: true
requirements:
  - REQ-042: Sign-Up API
---

# 9-02: Sign-Up API & Profile Logic

Implement the registration flow including Pydantic validation and the new `/auth/signup` endpoint.

## Tasks

<task id="1">
   <name>Define Auth Schemas</name>
   <files>
     - src/schemas/auth.py
   </files>
   <action>
     - Create `src/schemas/auth.py`:
       - `UserSignUp` with fields: `email`, `password`, `first_name`, `last_name`, `risk_tolerance`, `base_currency`, `middle_name`, `date_of_birth`, `display_name`, `avatar_url`, `bio`.
       - Add `field_validator` for `email` (to lowercase).
       - Add `field_validator` for `password` (regex: min 8, special char).
       - `UserResponse`: Comprehensive profile schema (no password).
   </action>
   <verify>
     - Verify Pydantic validation handles valid and invalid inputs (regex, email format).
   </verify>
   <done>
     - [ ] Auth schemas defined.
   </done>
</task>

<task id="2">
   <name>Implement Create User Service</name>
   <files>
     - src/services/auth.py
   </files>
   <action>
     - Update `src/services/auth.py`:
       - Implement `create_user(db: AsyncSession, data: UserSignUp) -> User`.
       - Check for email uniqueness before insert.
       - Raise `HTTPException(409)` if email exists.
       - Catch `IntegrityError` as a fallback.
   </action>
   <verify>
     - Inspect service logic for correct status assignment (PENDING) and error handling.
   </verify>
   <done>
     - [ ] Create user service implemented.
   </done>
</task>

<task id="3">
   <name>Implement Auth Controller</name>
   <files>
     - src/controllers/auth.py
   </files>
   <action>
     - Create `src/controllers/auth.py`:
       - `POST /signup`: Accepts `UserSignUp`, calls `create_user`, returns `UserResponse` with `201 Created`.
   </action>
   <verify>
     - Verify endpoint definition and response status.
   </verify>
   <done>
     - [ ] Auth controller implemented.
   </done>
</task>

<task id="4">
   <name>Register Router</name>
   <files>
     - main.py
   </files>
   <action>
     - Update `main.py`:
       - Include the `auth` router.
   </action>
   <verify>
     - `/docs` should show the new `/auth/signup` endpoint.
   </verify>
   <done>
     - [ ] Router registered.
   </done>
</task>

## Success Criteria
- Registration schema enforces password complexity.
- Email is automatically lowercased.
- `POST /auth/signup` creates a user in `PENDING` status.
- Duplicate email returns `409 Conflict`.
