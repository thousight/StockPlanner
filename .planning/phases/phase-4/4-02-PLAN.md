---
phase: phase-4
plan: 02
type: execute
wave: 2
depends_on: ["phase-4-01"]
files_modified: [src/controllers/chat.py, src/schemas/chat.py, src/main.py]
autonomous: true
requirements: [REQ-010, REQ-011]
must_haves:
  truths:
    - "The /chat endpoint returns a StreamingResponse with text/event-stream media type"
    - "Streaming events include token-level chunks and node transition status updates"
    - "Client disconnects result in immediate stop of the graph generation"
  artifacts:
    - path: "src/controllers/chat.py"
      provides: "SSE streaming logic and graph invocation"
    - path: "src/schemas/chat.py"
      provides: "API request/response schemas for chat"
  key_links:
    - from: "src/controllers/chat.py"
      to: "LangGraph.astream_events"
      via: "version='v2' call"
---

<objective>
Implement the core real-time communication channel between the user and the agentic graph. This plan focuses on the SSE streaming infrastructure, ensuring high responsiveness and reliable delivery of both agent tokens and status updates.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/phases/phase-4/phase-4-01-SUMMARY.md
@src/graph/graph.py
@src/services/context_injection.py
@src/graph/persistence.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Define Chat Schemas and SSE Models</name>
  <files>src/schemas/chat.py</files>
  <action>
    - Create `src/schemas/chat.py`.
    - Define `ChatRequest` schema: `message: str`, `thread_id: Optional[str]`.
    - Define SSE event payloads as Pydantic models: `ChatTokenEvent`, `ChatStatusEvent`, `ChatInterruptEvent`.
    - Ensure schemas align with the "Simplified UI Schema" decision in CONTEXT.md.
  </action>
  <verify>Check `src/schemas/chat.py` for correctly defined Pydantic models with type hints.</verify>
  <done>Standardized schemas for chat requests and streaming events are established.</done>
</task>

<task type="auto">
  <name>Task 2: Implement SSE Generator and /chat Endpoint</name>
  <files>src/controllers/chat.py, src/main.py</files>
  <action>
    - Create `src/controllers/chat.py`.
    - Implement `event_generator(request: Request, user_id: str, payload: ChatRequest)`:
        - Initialize `AsyncPostgresSaver` connection.
        - Fetch user portfolio context via `get_user_context_data`.
        - Invoke `graph.astream_events(..., version="v2")`.
        - Filter and yield SSE-formatted strings (`data: {json}

`) for tokens (`on_chat_model_stream`) and node starts (`on_chain_start`).
        - Implement disconnect check: `if await request.is_disconnected(): break`.
    - Register the router in `src/main.py`.
  </action>
  <verify>Use `curl -N -X POST /chat -H "X-User-ID: test-user" -d '{"message": "Hello"}'` and verify that the output is a stream of SSE data events containing tokens and status updates.</verify>
  <done>Users can initiate a streaming chat session that provides real-time feedback.</done>
</task>

<task type="auto">
  <name>Task 3: Implement Graceful Cancellation</name>
  <files>src/controllers/chat.py</files>
  <action>
    - Wrap the `astream_events` loop in a try/except block for `asyncio.CancelledError`.
    - Ensure any resources (DB connections, graph runs) are handled correctly when a client disconnects mid-stream.
    - Log cancellation events for monitoring.
  </action>
  <verify>Simulate a client disconnect (e.g., kill curl mid-stream) and verify the logs show the "Client disconnected, cancelling run" message.</verify>
  <done>The backend efficiently handles abandoned streams, preventing resource leaks.</done>
</task>

</tasks>

<verification>
Perform a full end-to-end test of the `/chat` endpoint using a streaming-capable client (curl or a simple python script) and verify that tokens arrive incrementally and node transitions are clearly identified.
</verification>

<success_criteria>
- `/chat` endpoint successfully streams tokens using SSE.
- `X-User-ID` header is required and used for context injection.
- Client disconnects are handled gracefully.
- LangGraph persistence tracks the thread across the stream.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-4/phase-4-02-SUMMARY.md`
</output>
