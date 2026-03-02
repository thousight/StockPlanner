---
phase: phase-4
plan: 03
type: execute
wave: 3
depends_on: ["phase-4-02"]
files_modified: [src/database/models.py, src/services/titler.py, src/controllers/threads.py, src/main.py]
autonomous: true
requirements: [REQ-013]
must_haves:
  truths:
    - "New chat threads are automatically assigned a descriptive title in the background"
    - "Users can retrieve a paginated list of their own chat threads"
    - "Chat history for a specific thread is returned in a simplified format (role, content, timestamp)"
  artifacts:
    - path: "src/services/titler.py"
      provides: "LLM-based thread titling logic"
    - path: "src/controllers/threads.py"
      provides: "Thread management and history retrieval endpoints"
  key_links:
    - from: "src/controllers/threads.py"
    - to: "AsyncPostgresSaver"
      via: "get_state calls for history"
---

<objective>
Enhance thread management by providing user-scoped thread isolation, descriptive auto-titling, and a performant history retrieval API. This ensures users can organize and revisit their financial conversations.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/phases/phase-4/phase-4-02-SUMMARY.md
@src/database/models.py
@src/graph/persistence.py
@src/schemas/chat.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement ChatThread Model and Titler Service</name>
  <files>src/database/models.py, src/services/titler.py</files>
  <action>
    - Add `ChatThread` model to `src/database/models.py`: `id` (UUID), `user_id`, `title`, `created_at`, `updated_at`.
    - Create `src/services/titler.py`.
    - Implement `generate_thread_title(user_msg: str, ai_msg: str) -> str` using a lightweight LLM call (gpt-4o-mini).
    - Implement a background task utility to update the `ChatThread` title after the first interaction.
  </action>
  <verify>Run a test that generates a title for a sample exchange and verifies it's 3-5 words as per RESEARCH.md.</verify>
  <done>Infrastructure for descriptive thread naming is in place.</done>
</task>

<task type="auto">
  <name>Task 2: Implement Thread Management Endpoints</name>
  <files>src/controllers/threads.py, src/main.py</files>
  <action>
    - Create `src/controllers/threads.py`.
    - Implement `GET /threads`: Returns a paginated list of `ChatThread` records for the current `user_id`.
    - Implement `DELETE /threads/{thread_id}`: Soft-deletes a thread.
    - Register the router in `src/main.py`.
  </action>
  <verify>Use curl to create a thread (via `/chat`), then verify it appears in `GET /threads` with the correct `user_id`.</verify>
  <done>Users can view and manage their conversation history.</done>
</task>

<task type="auto">
  <name>Task 3: Implement Paginated History Retrieval</name>
  <files>src/controllers/threads.py</files>
  <action>
    - Implement `GET /threads/{thread_id}/messages`:
        - Fetch checkpoints from `AsyncPostgresSaver` for the given `thread_id`.
        - Extract messages from the latest state.
        - Map to `Simplified UI Schema`: `{role, content, timestamp}`.
        - Support pagination parameters (`limit`, `before_timestamp`).
  </action>
  <verify>Fetch messages for an existing thread and verify the schema matches the "Simplified UI Schema" decision.</verify>
  <done>Conversations can be resumed or reviewed with a clean, mobile-optimized history API.</done>
</task>

</tasks>

<verification>
Verify that new threads appear in the list with titles, and that individual thread history is correctly paginated and formatted.
</verification>

<success_criteria>
- Threads are user-isolated via `X-User-ID`.
- Auto-titling runs in the background for new threads.
- History retrieval follows the Simplified UI Schema and supports pagination.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-4/phase-4-03-SUMMARY.md`
</output>
