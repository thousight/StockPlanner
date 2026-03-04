# Context - Phase 14: Protocol Compliance

This document captures implementation decisions for refactoring the streaming API to be fully compliant with the official LangGraph API protocol.

## 1. Protocol Alignment
- **Event Types:** Support the standard set of LangGraph SSE events: `metadata`, `messages`, `values`, and `end`.
- **Payload Format:** 
    - Use full `AIMessageChunk` structures for token streaming.
    - Emit `metadata` events at the start of each node execution (including subgraphs).
    - Support `values` events to yield the full `AgentState` after node completion.
- **Completion Pattern:** Explicitly emit an `event: end` tag before closing the stream.

## 2. API Transformation
- **Breaking Change:** A "Breaking Switch" is approved. The existing custom `/chat` endpoint will be removed.
- **New Standard Endpoint:** Implement `POST /threads/{thread_id}/runs/stream` to match the official LangGraph API pathing.
- **Cleanup:** Delete legacy `ChatTokenEvent`, `ChatStatusEvent`, and other simplified custom schemas once the new protocol is verified.

## 3. Negotiation & Subgraphs
- **Stream Mode:** The client will request desired modes (e.g., `["messages", "metadata"]`) via a `stream_mode` field in the request body.
- **Subgraph Support:** Ensure the streaming logic correctly handles and yields events from nested subgraphs (like the Analyst debate).
- **Interrupts:** Implement support for the `interrupt` event type, ensuring the Dart SDK can natively handle future human-in-the-loop interactions.

## 4. History & Backfill
- **Backfill Compliance:** The "on-the-fly" backfill logic (from Phase 13) must be updated to emit messages using the standard protocol format (`event: messages`).
- **Idempotency:** Maintain the `langchain_msg_id` uniqueness while conforming to the new output stream.
