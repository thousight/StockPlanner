---
phase: phase-4
plan: 04
type: execute
wave: 4
depends_on: ["phase-4-03"]
files_modified: [src/graph/nodes.py, src/controllers/chat.py]
autonomous: true
requirements: [REQ-011]
must_haves:
  truths:
    - "The graph pauses execution when high-risk recommendations are made, waiting for user approval"
    - "Interrupt events are surfaced via SSE to notify the client of the pause"
    - "A dedicated /resume endpoint allows the user to provide feedback and continue the graph execution"
  artifacts:
    - path: "src/controllers/chat.py"
      provides: "Resume endpoint and interrupt event streaming"
    - path: "src/graph/agents/analyst/agent.py"
      provides: "Mandatory confirmation breakpoints"
  key_links:
    - from: "src/graph/agents/analyst/agent.py"
      to: "LangGraph.interrupt"
      via: "function call"
---

<objective>
Implement Human-in-the-Loop patterns to ensure safety and completeness in financial advice. This plan adds mandatory breakpoints for high-risk recommendations and provides the mechanism for users to approve or correct the agent's plan before final synthesis.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/phases/phase-4/phase-4-03-SUMMARY.md
@src/graph/graph.py
@src/controllers/chat.py
@src/graph/agents/analyst/agent.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add Interrupt Points to Analyst Agent</name>
  <files>src/graph/agents/analyst/agent.py</files>
  <action>
    - Update `analyst_agent` to include a `requires_confirmation` check.
    - If the analyst recommends a specific trade or high-risk strategy, invoke `interrupt()` with a descriptive message.
    - Ensure the state is correctly checkpointed at the interrupt point.
  </action>
  <verify>Invoke the graph with a prompt that triggers a recommendation and verify the graph status is 'suspended' in the checkpointer.</verify>
  <done>Safety breakpoints are integrated into the analytical workflow.</done>
</task>

<task type="auto">
  <name>Task 2: Surface Interrupts in SSE Stream</name>
  <files>src/controllers/chat.py</files>
  <action>
    - Update the SSE `event_generator` in `src/controllers/chat.py` to detect interrupt events.
    - When an interrupt is detected (via `on_chain_stream` with `__interrupt__` or state inspection), yield a `ChatInterruptEvent` containing the interrupt message.
  </action>
  <verify>Run a chat that triggers an interrupt and verify the client receives a 'data: {"type": "interrupt", ...}' event.</verify>
  <done>Clients are notified in real-time when the agent requires human input.</done>
</task>

<task type="auto">
  <name>Task 3: Implement /resume Endpoint</name>
  <files>src/controllers/chat.py</files>
  <action>
    - Implement `POST /chat/{thread_id}/resume`:
        - Accepts `user_response: str` (e.g., "approved", "cancel", or a correction).
        - Uses `graph.update_state` to provide the user response to the waiting node.
        - Re-invokes the graph stream from the checkpoint.
        - Returns a `StreamingResponse` for the remainder of the execution.
  </action>
  <verify>Trigger an interrupt, then call `/resume` and verify the graph continues and produces a final summary.</verify>
  <done>Users can interactively guide and approve agentic financial plans.</done>
</task>

</tasks>

<verification>
Perform a full Human-in-the-Loop flow: 
1. Ask for a recommendation.
2. Observe the stream pausing at the interrupt event.
3. Call /resume with "approved".
4. Observe the stream finishing the response.
</verification>

<success_criteria>
- Interrupts are correctly triggered for high-risk advice.
- Interrupt events are delivered via SSE.
- The `/resume` endpoint correctly continues the execution with user input.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-4/phase-4-04-SUMMARY.md`
</output>
