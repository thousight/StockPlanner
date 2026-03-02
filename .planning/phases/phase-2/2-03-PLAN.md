---
phase: phase-2
plan: 2-03
type: execute
wave: 3
depends_on: [2-02]
files_modified: [src/graph/state.py, src/graph/graph.py, src/graph/nodes.py, src/main.py]
autonomous: true
requirements: [REQ-012, REQ-023]
user_setup: []
must_haves:
  truths:
    - "Reports are only committed to the database upon successful graph completion"
    - "The API rejects concurrent requests to the same thread_id"
  artifacts:
    - path: "src/graph/state.py"
      provides: "Updated AgentState with pending data"
    - path: "src/graph/nodes.py"
      provides: "Final commit node implementation"
  key_links:
    - from: "src/graph/graph.py"
      to: "src/graph/nodes.py"
      via: "commit_node entry"
      pattern: "add_node\(['"]commit['"], commit_node\)"
---

<objective>
Implement the Propose-Commit pattern in LangGraph to ensure transaction integrity for persistent data (Reports) and add concurrency protection for active threads.

Purpose: Prevents partial/failed results from polluting the primary database and avoids state corruption from concurrent runs.
Output: Refactored graph with success-only commit logic and thread locking.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phase-2/2-CONTEXT.md
@.planning/phase-2/2-RESEARCH.md
@src/graph/state.py
@src/graph/graph.py
@src/database/models.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Refactor AgentState for Propose-Commit</name>
  <files>src/graph/state.py</files>
  <action>
    1. Update `AgentState` in `src/graph/state.py` to include `pending_report` (Optional[dict/model]).
    2. This field will hold the synthesized report data during the graph run without writing to the database.
  </action>
  <verify>
    Ensure `AgentState` includes the new field and it is serializable.
  </verify>
  <done>
    Agent state is prepared to support the Propose-Commit pattern.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement Commit Node and Graph Update</name>
  <files>src/graph/nodes.py, src/graph/graph.py</files>
  <action>
    1. Implement `commit_node` in `src/graph/nodes.py` (or relevant file):
       - It reads `pending_report` from the state.
       - It writes the report to the `Reports` table using an async session.
       - It clears the `pending_report` from the state after successful write.
    2. Update `src/graph/graph.py`:
       - Add the `commit` node to the graph.
       - Ensure all paths to completion (where a report is generated) lead to the `commit` node.
       - Use `END` as the successor to the `commit` node.
  </action>
  <verify>
    Run a test graph execution and verify that a record appears in the `Reports` table only at the end.
  </verify>
  <done>
    Synthesized reports are persisted only upon successful completion of the agentic workflow.
  </done>
</task>

<task type="auto">
  <name>Task 3: Implement Thread Concurrency Protection</name>
  <files>src/main.py</files>
  <action>
    1. Implement a simple in-memory lock or check for active `thread_id` in the API (or use LangGraph's native concurrency handling if applicable, but CONTEXT.md asks for explicit rejection).
    2. Add middleware or logic to the future `/chat` endpoint (can be a placeholder in `src/main.py` for now or a utility) to return 409 Conflict if a `thread_id` is already processing.
    3. Since `/chat` isn't fully implemented, add the foundational utility for this check.
  </action>
  <verify>
    Verify that trying to access the same thread twice (simulated) results in an appropriate error or wait.
  </verify>
  <done>
    The API is protected against concurrent state corruption for the same conversation thread.
  </done>
</task>

</tasks>

<verification>
Check `Reports` table after a successful run. Attempt concurrent runs to verify 409.
</verification>

<success_criteria>
- Reports only persist on graph success.
- Concurrent requests to the same `thread_id` are rejected.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-2/phase-2-03-SUMMARY.md`
</output>
