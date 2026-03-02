# Context - Phase 4: Agentic Chat Streaming

This document captures implementation decisions for Phase 4 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Streaming Event Protocol
- **Schema:** Adopt the standard **LangGraph SSE event schema** (`event`, `data`, `metadata`) for maximum compatibility.
- **Granularity:** 
  - Stream **Raw Tokens** word-by-word for high-responsiveness.
  - Send **Node Transitions** (e.g., "Supervisor -> Analyst") to update the mobile UI status.
- **Progress Detail:** Maintain **Minimal Progress** indicators; focus on streaming agent text and state changes rather than verbose tool-call logs.

## 2. Thread Initialization & Context
- **Identity:** User identity is **Derived from Auth** (using the `X-User-ID` header as a bridge until Milestone 2).
- **Profile Injection:** Automatically fetch and **Auto-Inject** the user's latest portfolio summary (holdings, sector allocation, and PNL from Phase 3) into the system prompt for every new chat interaction.
- **Orchestration:** The **Supervisor agent** maintains full control over the initial focus and routing; no user-specified focus parameter is required at thread start.
- **IDs:** Thread IDs must be **Server-Generated** upon the first message of a new conversation and returned to the client.

## 3. Human-in-the-Loop & Interrupts
- **Missing Data:** If an agent identifies missing critical information, the graph will **Pause & Wait** for user input via an explicit "interrupt" SSE event.
- **Cancellation:** Support **Graceful Cancel** of running streams, ensuring the LangGraph thread is properly checkpointed and cleaned up before stopping.
- **Corrections:** **Allow Interrupts** and user corrections mid-flow; the system should be able to process new user messages that modify the current agentic plan.
- **Safety Breakpoints:** Implement **Mandatory Confirmation** breakpoints for high-risk financial advice or recommendations, requiring explicit user approval before the graph proceeds to final synthesis.

## 4. History & Thread Management
- **Auto-Titling:** Enable **Auto-Title** generation; the backend will summarize the initial interaction to create a descriptive thread title.
- **History Schema:** Historical messages are returned using a **Simplified UI Schema** (`{role, content, timestamp}`) optimized for the Flutter frontend.
- **Persistence:** Historical chat retrieval must be **Paginated** to ensure performance for long-running threads.
- **Metadata Depth:** Conversation history will focus on **Simple Text History**, omitting internal adversarial arguments or confidence scores from the primary UI view.
