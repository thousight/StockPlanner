# Context - Phase 13: History Management

This document captures implementation decisions for establishing permanent conversation history in PostgreSQL and exposing management APIs.

## 1. Storage Schema & Content
- **Message Scope:** Store only the final messages exchanged between the User and the AI. Internal agent thoughts, tool outputs, and intermediate reasoning steps remain transient in Redis.
- **Role Mapping:** Simplify all agent outputs to the role of **"AI"**. User inputs are labeled as **"Human"**.
- **Metadata:** No structured metadata or token usage metrics will be stored in the relational table for this phase.
- **Persistence:** Use a `chat_messages` table in PostgreSQL with standard text content and timestamps.

## 2. Synchronization Logic
- **Trigger:** Synchronization occurs asynchronously as a FastAPI **Background Task** triggered immediately after the LangGraph response completes.
- **Content Integrity:** Only successfully completed exchanges are promoted to permanent storage.
- **Revision Handling:** In scenarios where agents perform multiple revisions, only the **final version** presented to the user is persisted.
- **Data Backfill:** The system will attempt to backfill history for existing threads that currently reside only in Redis/Postgres checkpointer state during the first interaction after this feature is deployed.

## 3. Retrieval & Management UX
- **Sorting:** History retrieval will return messages in **Reverse Chronological** order (newest first).
- **Pagination:** Implement **Cursor-based pagination** to optimize for mobile infinite scrolling performance.
- **Deletion:** Deleting a thread or message will perform a **Soft Delete** only, preserving the underlying data for the standard retention period (as defined in Milestone 2).
- **Scope:** Retrieval is strictly **Thread-based**; global search across all threads is not required for this phase.

## 4. Multi-Tenancy
- **Ownership:** Every message record must be strictly linked to a `user_id` and `thread_id`.
- **Enforcement:** Standard "Stealth 404" logic applies to unauthorized attempts to retrieve history for a thread the user does not own.
