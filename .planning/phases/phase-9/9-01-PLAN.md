---
phase: phase-9
plan: 9-01
type: execute
wave: 1
depends_on: []
must_haves:
  truths:
    - Argon2id password hashing is the project standard for user security.
    - UUIDv7 is the primary key format for the User model.
  artifacts:
    - path: src/database/models.py
      provides: User model with partial unique email index.
      min_lines: 50
    - path: src/services/auth.py
      provides: argon2-cffi based password hashing.
      min_lines: 20
  key_links:
    - from: Phase 9
      to: REQ-040
      via: Argon2id implementation in auth service.
    - from: Phase 9
      to: REQ-041
      via: User SQLAlchemy model with UUIDv7 primary key.
files_modified:
  - src/database/models.py
  - src/services/auth.py
  - requirements.txt
autonomous: true
requirements:
  - REQ-040: Secure Password Hashing (Argon2id)
  - REQ-041: User Model (UUIDv7)
---

# 9-01: User Schema & Password Hashing

Establish the data foundation for user management, including the secure User model and password hashing utilities.

## Tasks

<task id="1">
   <name>Install Dependencies</name>
   <files>
     - requirements.txt
   </files>
   <action>
     - Add `argon2-cffi` and `uuid-utils` to `requirements.txt`.
     - Install dependencies in the local environment.
   </action>
   <verify>
     - `pip show argon2-cffi uuid-utils` should succeed.
   </verify>
   <done>
     - [ ] Dependencies added and installed.
   </done>
</task>

<task id="2">
   <name>Define User Model</name>
   <files>
     - src/database/models.py
   </files>
   <action>
     - Update `src/database/models.py`:
       - Add `UserStatus` Enum (`PENDING`, `ACTIVE`, `DEACTIVATED`).
       - Add `RiskTolerance` Enum (`CONSERVATIVE`, `MODERATE`, `AGGRESSIVE`).
       - Create `User` class with UUIDv7 primary key and profile fields.
       - Add audit fields: `created_at`, `updated_at`, `last_login_at`, `deleted_at`.
       - Implement partial unique index: `Index("ix_user_email_unique", "email", unique=True, postgresql_where=(deleted_at == None))`.
   </action>
   <verify>
     - Inspect `src/database/models.py` for correct types and partial index.
   </verify>
   <done>
     - [ ] User model defined with partial index.
   </done>
</task>

<task id="3">
   <name>Implement Hashing Service</name>
   <files>
     - src/services/auth.py
   </files>
   <action>
     - Create `src/services/auth.py`.
     - Initialize `PasswordHasher` from `argon2`.
     - Implement `hash_password(password: str) -> str`.
     - Implement `verify_password(hashed: str, password: str) -> bool`.
   </action>
   <verify>
     - Verify hashing functions correctly handle matches and mismatches via a small script or CLI test.
   </verify>
   <done>
     - [ ] Hashing service implemented.
   </done>
</task>

<task id="4">
   <name>Database Migration</name>
   <files>
     - migrations/versions/
   </files>
   <action>
     - Run `alembic revision --autogenerate -m "Add user table"`.
     - Review and verify the generated script.
     - Apply migration: `alembic upgrade head`.
   </action>
   <verify>
     - Check database for the presence of the `users` table and its partial index.
   </verify>
   <done>
     - [ ] Migration generated and applied.
   </done>
</task>

## Success Criteria
- `requirements.txt` updated.
- `User` model is correctly mapped in SQLAlchemy with a soft-delete safe unique index.
- Hashing functions verified to work with Argon2id.
- Migration successfully applied to the database.
