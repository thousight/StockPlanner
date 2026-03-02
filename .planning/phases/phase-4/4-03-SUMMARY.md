# Plan Summary - Phase 4-03: Thread Lifecycle & History

## Implementation Summary
Successfully implemented the thread lifecycle and history management system, fulfilling REQ-012 and REQ-013. The API now supports persistent conversation metadata, automated titling, and simplified history retrieval optimized for the mobile client.

- **Thread Metadata Model**: Added the `ChatThread` model to `src/database/models.py` to store high-level conversation metadata (`user_id`, `title`, timestamps, and a soft-delete flag) separately from the raw LangGraph state.
- **Auto-Titling Service**: Created `src/services/titler.py` utilizing the `gpt-4o-mini` model to generate concise, 3-5 word descriptive titles based on the initial user-assistant interaction. This service runs as a background task.
- **Thread Management Controllers**:
  - `GET /threads`: Fetches a paginated list of active threads for a specific user.
  - `DELETE /threads/{id}`: Performs a soft-deletion of a thread.
  - `GET /threads/{id}/messages`: Connects directly to the `AsyncPostgresSaver` checkpointer, extracts the raw `messages` from the LangGraph state, and transforms them into a clean, simplified `{role, content, timestamp}` schema for the Flutter UI.
- **Chat Integration**: Updated the `/chat` endpoint to automatically create a `ChatThread` record on the first message and trigger the background titling task once the agent responds.

## File Changes
- `src/database/models.py`: Added `ChatThread` model.
- `src/services/titler.py`: New auto-titling service.
- `src/controllers/threads.py`: New endpoints for managing threads and fetching history.
- `src/schemas/threads.py`: Pydantic schemas for the thread endpoints.
- `src/controllers/chat.py`: Integrated thread creation and background titling.
- `src/main.py`: Registered the `threads` router.

## Technical Decisions
- **Separation of Metadata and State**: By separating high-level thread metadata (`ChatThread`) from the granular LangGraph state (`checkpoints` table), we ensure that the mobile app can quickly load a user's chat history list without querying large, serialized state blobs.
- **Simplified UI Schema**: The `GET /threads/{id}/messages` endpoint intentionally strips out complex agentic data (like tool calls, internal thoughts, or confidence scores), ensuring the mobile client only receives what is necessary to render the chat bubble interface.
- **Background Tasks**: The auto-titler is executed as a FastAPI `BackgroundTasks` function to prevent any latency in the main chat response.

## Verification
- Alembic migration generated and applied for `ChatThread`.
- Endpoints verified to return expected structures.
- Auto-titler confirmed to generate appropriate titles using `gpt-4o-mini`.
