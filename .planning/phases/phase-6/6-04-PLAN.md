---
phase: phase-6
plan: 6-04
type: execute
wave: 3
depends_on: [6-02]
files_modified: [tests/api/test_chat_streaming.py, tests/api/test_chat_resilience.py]
autonomous: true
requirements: [REQ-032]

must_haves:
  truths:
    - "Chat endpoint streams tokens correctly via SSE using mocked graph events"
    - "Server-side resources are cleaned up when an SSE client disconnects"
  artifacts:
    - path: "tests/api/test_chat_streaming.py"
      provides: "Verification of token-level SSE streaming"
    - path: "tests/api/test_chat_resilience.py"
      provides: "Verification of client disconnect handling in streams"
  key_links:
    - from: "tests/api/test_chat_streaming.py"
      to: "LangGraph .astream_events"
      via: "AsyncGenerator mock"
    - from: "tests/api/test_chat_resilience.py"
      to: "FastAPI Request.is_disconnected"
      via: "Context manager exit simulation"
---

<objective>
Verify the real-time streaming capabilities of the agentic chat and its resilience to client-side failures.

Purpose: Ensure that the most complex API interaction (SSE streaming) is robust and correctly implemented.
Output: Verified streaming logic and disconnect handling.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-6/6-02-PLAN.md
@.planning/phases/phase-6/6-CONTEXT.md
@.planning/phases/phase-6/6-RESEARCH.md
@src/controllers/chat.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: /chat SSE Streaming Tests</name>
  <files>tests/api/test_chat_streaming.py</files>
  <action>
    Implement tests for the streaming chat endpoint:
    1.  Create `tests/api/test_chat_streaming.py`.
    2.  Mock the LangGraph `.astream_events()` method to return an async generator yielding deterministic SSE events (e.g., `on_chat_model_stream` with specific tokens).
    3.  Use `async with client.stream("POST", "/chat", ...)` to consume the stream.
    4.  Verify that all tokens are received and the stream terminates correctly.
    5.  Verify that the response content-type is `text/event-stream`.
  </action>
  <verify>Run `pytest tests/api/test_chat_streaming.py`.</verify>
  <done>Token-level streaming is verified using deterministic graph event mocks.</done>
</task>

<task type="auto">
  <name>Task 2: SSE Client Disconnect & Abort Resilience</name>
  <files>tests/api/test_chat_resilience.py</files>
  <action>
    Verify that the server handles aborted connections gracefully:
    1.  Create `tests/api/test_chat_resilience.py`.
    2.  Implement a test that starts a stream and then exits the `async with client.stream` block prematurely.
    3.  In the mocked graph generator, use `try/finally` or periodic `await request.is_disconnected()` checks to detect the abort.
    4.  Verify (using a mock or a side-effect flag) that the server-side cleanup logic is triggered.
    5.  Reference "Pitfall 2" in 6-RESEARCH.md for implementation details.
  </action>
  <verify>Run `pytest tests/api/test_chat_resilience.py`.</verify>
  <done>The application correctly detects and handles SSE client disconnects without resource leaks.</done>
</task>

</tasks>

<verification>
Check for proper use of `aiter_lines()` or similar to consume the stream.
Ensure that the disconnect test doesn't hang (use `asyncio.wait_for` if necessary).
</verification>

<success_criteria>
- SSE stream yields expected content from mocked graph events.
- Client disconnect is detected server-side and triggers cleanup logic.
- No hanging tests or shared state between streaming test runs.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-6/phase-6-6-04-SUMMARY.md`
</output>
