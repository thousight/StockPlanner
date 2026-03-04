# Requirements - Milestone 3: Conversation History & Memory

This milestone focuses on enhancing the agentic memory performance using Redis and establishing a permanent, queryable conversation history in PostgreSQL for the UI.

## 1. High-Speed Memory (Redis)

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-070** | **Redis Stack Integration**: Provision and connect to a Redis Stack (RedisJSON + RediSearch) instance on Railway. | P0 | Completed |
| **REQ-071** | **LangGraph Redis Checkpointer**: Replace the current PostgreSQL checkpointer with `AsyncRedisSaver` for lower latency state management. | P0 | Completed |
| **REQ-072** | **Lifespan Connection Management**: Properly initialize and close Redis connections within the FastAPI lifespan context. | P1 | Completed |

## 2. Permanent History (PostgreSQL)

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-080** | **Relational Message Schema**: Implement a `chat_messages` table in PostgreSQL to store simplified, human-readable conversation history. | P0 | Completed |
| **REQ-081** | **Dual-Write Synchronization**: Ensure the final user-AI exchange is saved to the relational database upon completion of a graph run. | P0 | Completed |
| **REQ-082** | **Message Ownership**: Enforce strict user ownership of message history (FK to `users.id`). | P0 | Completed |

## 3. History Management APIs

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-090** | **List Conversation History**: Endpoint to retrieve a paginated list of human-readable messages for a specific `thread_id`. | P0 | Completed |
| **REQ-091** | **Delete Message/Thread**: Endpoints to permanently remove specific messages or entire conversation histories from PostgreSQL. | P1 | Completed |

## Success Criteria

- [x] LangGraph state is successfully persisted to Redis and can be resumed across requests.
- [x] Conversations are readable from the PostgreSQL `chat_messages` table, separate from the binary LangGraph state.
- [x] Users can retrieve their simplified chat history via a new `/history` or updated `/threads` API.
- [x] Unauthorized users cannot access the history of threads they do not own.
- [x] Redis connection stability is verified under concurrent request load.
