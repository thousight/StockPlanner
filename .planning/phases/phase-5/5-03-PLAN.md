---
phase: 05-agentic-flow-refinement
plan: 5-03
type: execute
wave: 3
depends_on: [5-02]
files_modified: [src/graph/graph.py, src/graph/nodes.py, src/schemas/chat.py, src/controllers/chat.py]
autonomous: true
requirements: [REQ-011, REQ-013]
---

<objective>
Refine agentic flow with conditional interrupts, rejection handling, and enhanced SSE streaming.
Purpose: Improve UX by reducing unnecessary breaks and providing rich metadata during interrupts.
Output: Conditional graph breakpoints, Acknowledge & Continue logic, and updated SSE event types.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-5/5-CONTEXT.md
@src/graph/graph.py
@src/graph/nodes.py
@src/schemas/chat.py
@src/controllers/chat.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Conditional Interrupts & Rejection Handling</name>
  <files>src/graph/graph.py, src/graph/nodes.py</files>
  <action>
    - Refactor `create_graph` in `src/graph/graph.py`:
      - Remove static `interrupt_before=["commit"]`.
      - Use `interrupt()` inside a new `safety_node` or before `commit_node` based on `complexity_score`.
    - Refine `commit_node` in `src/graph/nodes.py`:
      - Handle "Acknowledge & Continue" pattern: if resume signal is "reject", set `pending_report` to `None` and return an acknowledgment in the `output` field.
      - If complexity threshold is met, use `interrupt()` to request approval.
      - Ensure `Off-Topic` agent results never generate reports.
  </action>
  <verify>Run the graph with a simple prompt (low complexity) and verify it completes without interrupt. Run with a complex prompt (or action keywords) and verify it interrupts.</verify>
  <done>Interrupts are conditional on complexity and action keywords, and rejections are handled gracefully.</done>
</task>

<task type="auto">
  <name>Task 2: Enhanced SSE Streaming & Silent Updates</name>
  <files>src/schemas/chat.py, src/controllers/chat.py</files>
  <action>
    - Update `ChatInterruptEvent` in `src/schemas/chat.py` to include `full_preview` (Title, Topic, Category).
    - Add `ChatUpdateEvent` to `src/schemas/chat.py` for "Silent Updates".
    - Update `handle_interrupts` in `src/controllers/chat.py`:
      - Fetch `pending_report` metadata from the graph state to populate the `full_preview` in the SSE event.
    - Update `event_generator` to yield `ChatUpdateEvent` when a report is auto-committed (silent commit).
  </action>
  <verify>Test SSE stream: verify `interrupt` events contain report metadata and `update` events are sent for auto-commits.</verify>
  <done>SSE streaming provides full context for interrupts and notifies the client of background data updates.</done>
</task>

</tasks>

<verification>
End-to-end test of the chat flow: verify conditional interrupts, metadata visibility, and searchability of the resulting reports.
</verification>

<success_criteria>
- Simple chats bypass interrupts; complex/financial ones trigger them.
- Interrupt payloads include report previews (Title, Topic, Category).
- Rejections don't crash the turn; they acknowledge and end/continue smoothly.
- Silent update events are sent for auto-commits.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-5/5-03-SUMMARY.md`
</output>
