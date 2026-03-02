# Phase 4: Agentic Chat Streaming - Research

**Researched:** 2026-03-02
**Domain:** LangGraph SSE Streaming, Human-in-the-Loop, Context Injection
**Confidence:** HIGH

## Summary

This research establishes the technical foundation for transforming the StockPlanner multi-agent graph into a production-grade streaming API. The core approach utilizes FastAPI's `StreamingResponse` paired with LangGraph's `astream_events` (v2) to provide token-level responsiveness and real-time agent status updates to a mobile client.

**Primary recommendation:** Use `astream_events(version="v2")` to capture granular token chunks and node transitions, while implementing proactive disconnection checks and `asyncio.CancelledError` handling to ensure graceful resource cleanup.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Schema:** Adopt the standard **LangGraph SSE event schema** (`event`, `data`, `metadata`) for maximum compatibility.
- **Granularity:** 
  - Stream **Raw Tokens** word-by-word for high-responsiveness.
  - Send **Node Transitions** (e.g., "Supervisor -> Analyst") to update the mobile UI status.
- **Identity:** User identity is **Derived from Auth** (using the `X-User-ID` header as a bridge until Milestone 2).
- **Profile Injection:** Automatically fetch and **Auto-Inject** the user's latest portfolio summary into the system prompt for every new chat interaction.
- **Orchestration:** The **Supervisor agent** maintains full control over the initial focus and routing; no user-specified focus parameter is required at thread start.
- **IDs:** Thread IDs must be **Server-Generated** upon the first message of a new conversation and returned to the client.
- **Missing Data:** If an agent identifies missing critical information, the graph will **Pause & Wait** for user input via an explicit "interrupt" SSE event.
- **Cancellation:** Support **Graceful Cancel** of running streams.
- **Safety Breakpoints:** Implement **Mandatory Confirmation** breakpoints for high-risk financial advice or recommendations.
- **Auto-Titling:** Enable **Auto-Title** generation based on the initial interaction.
- **Persistence:** Use `AsyncPostgresSaver` for thread persistence.
- **History Schema:** Historical messages use a **Simplified UI Schema** (`{role, content, timestamp}`).

### Claude's Discretion
- **Progress Detail:** Maintain **Minimal Progress** indicators; focus on streaming agent text and state changes rather than verbose tool-call logs.
- **Corrections:** **Allow Interrupts** and user corrections mid-flow; the system should be able to process new user messages that modify the current agentic plan.
- **History Pagination:** Chat retrieval must be **Paginated** for performance.
- **Metadata Depth:** Focus on **Simple Text History**, omitting internal adversarial arguments.

### Deferred Ideas (OUT OF SCOPE)
- **Advanced UI Animations:** Animations for agent state changes (deferred to frontend).
- **Full Auth System:** Milestone 2 scope.
- **Adversarial Confidence Scores:** Omitted from primary UI view.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| **REQ-010** | **`/chat` Streaming Endpoint** | SSE schema and FastAPI `StreamingResponse` pattern verified. |
| **REQ-011** | **LangGraph Orchestration** | Integration via `astream_events` v2 with node transition tracking. |
| **REQ-012** | **State Persistence (Checkpointer)** | `AsyncPostgresSaver` usage confirmed for multi-turn conversations. |
| **REQ-013** | **Thread Management** | Thread IDs and background auto-titling pattern defined. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | ^0.100+ | Web framework | Best-in-class async support for SSE. |
| LangGraph | ^0.2.0+ | Agent orchestration | State-of-the-art for multi-agent loops and human-in-the-loop. |
| SQLAlchemy | ^2.0+ | Database ORM | Required for financial data and portfolio fetching. |
| psycopg | ^3.1+ | Async PG driver | Required for `AsyncPostgresSaver` connectivity. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|--------------|
| Pydantic | ^2.0+ | Data validation | Defining SSE event schemas and API requests. |
| LangChain OpenAI | ^0.1.0+ | LLM connectivity | Primary model interface for gpt-4o / gpt-4o-mini. |

## Architecture Patterns

### Recommended Project Structure
```
src/
├── controllers/
│   └── chat.py          # /chat endpoint and SSE generator
├── services/
│   ├── portfolio.py     # Existing: portfolio summary logic
│   └── titler.py        # NEW: Background auto-titling service
├── graph/
│   ├── persistence.py   # NEW: AsyncPostgresSaver setup
│   ├── state.py         # Updated: user_context population
│   └── utils/
│       └── prompt.py    # Updated: context injection logic
```

### Pattern 1: FastAPI SSE Generator (LangGraph v2)
**What:** Wrapping `astream_events` in an async generator that yields SSE-formatted strings.
**When to use:** For all real-time chat interactions.
**Example:**
```python
async def event_generator(inputs, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    async for event in graph.astream_events(inputs, config, version="v2"):
        # Filter for relevant events (tokens, node starts, interrupts)
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield f"data: {json.dumps({'type': 'token', 'content': content})}

"
        elif kind == "on_chain_start" and "langgraph_node" in event["metadata"]:
            node = event["metadata"]["langgraph_node"]
            yield f"data: {json.dumps({'type': 'status', 'content': f'Agent {node} working...'})}

"
```

### Pattern 2: Graceful Disconnect & Cancellation
**What:** Detecting client disconnect and propagation of `CancelledError`.
**When to use:** Mandatory for all streaming endpoints to prevent zombie agent runs.
**Example:**
```python
@app.post("/chat")
async def chat(request: Request, payload: ChatRequest):
    async def stream():
        try:
            async for event in graph.astream_events(...):
                if await request.is_disconnected():
                    break
                yield ...
        except asyncio.CancelledError:
            # Graph will stop at next super-step
            logger.info("Client disconnected, cancelling run.")
            raise
    return StreamingResponse(stream(), media_type="text/event-stream")
```

### Pattern 3: Human-in-the-Loop Interrupts
**What:** Surfacing `interrupt()` calls from the graph as SSE events.
**When to use:** When missing critical data or requiring safety confirmation.
**Detection:** Monitor `on_chain_stream` events for the `__interrupt__` key in `data['chunk']`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSE Protocol | Custom formatting | `data: {json}

` | SSE is a strict spec; hand-rolling newlines often causes client parsing errors. |
| Persistence | Custom DB schema | `AsyncPostgresSaver` | LangGraph persistence handles serialization, checkpointing, and forks automatically. |
| Portfolio Aggregation | New logic in Graph | `portfolio_service.get_portfolio_summary` | Maintain a single source of truth for financial calculations. |
| Async DB Pool | Global session objects | FastAPI Dependencies + `AsyncSession` | Ensures proper cleanup and connection pooling on Railway. |

## Common Pitfalls

### Pitfall 1: Token Bloat in Context Injection
**What goes wrong:** Injecting the entire transaction history (JSON) into the system prompt for every turn.
**How to avoid:** Format a concise text-based "Portfolio Summary" instead of raw data.
**Warning signs:** High latency on the first response and "context window" warnings in logs.

### Pitfall 2: Blocking Generative Stream with Sync DB Calls
**What goes wrong:** Calling a synchronous `db.query()` inside the async generator.
**How to avoid:** Always use `await db.execute(select(...))` or move data fetching *before* starting the stream.

### Pitfall 3: Checkpoint Deadlocks
**What goes wrong:** Multiple requests for the same `thread_id` attempting to write checkpoints simultaneously.
**How to avoid:** LangGraph handles this by design, but ensure the UI prevents "double-submit" of messages before the stream ends.

## Code Examples

### Portfolio Summary Template
```python
def format_portfolio_for_llm(summary: PortfolioSummary) -> str:
    """
    Injected into AgentState.user_context['portfolio_summary']
    """
    return f"""
    Current Portfolio Status:
    - Total Value: ${summary.total_value_usd:,.2f}
    - Cost Basis: ${summary.total_cost_basis_usd:,.2f}
    - Total Gain/Loss: ${summary.total_gain_loss_usd:,.2f} ({summary.total_gain_loss_pct:.2f}%)
    - Daily Change: ${summary.daily_pnl_usd:,.2f} ({summary.daily_pnl_pct:.2f}%)
    - Top Sectors: {', '.join([f"{s.sector} ({s.percentage:.1f}%)" for s in summary.sector_allocation[:3]])}
    """
```

### Auto-Titling Prompt
```python
TITLER_PROMPT = """
Summarize the initial exchange between a user and a financial AI into a catchy, 3-5 word title.
Return ONLY the title text. No quotes, no prefix.

User: {user_msg}
AI: {ai_msg}

Title:"""
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `astream` | `astream_events(v2)` | 2024 | Better filtering for specific LLM outputs vs tool outputs. |
| `interrupt_before` | `interrupt()` | LangGraph 0.2 | Precise control over *where* the graph pauses inside a node. |
| MemorySaver | `AsyncPostgresSaver` | Production standard | Persistent state across server restarts/deployments. |

## Open Questions

1. **How to handle "Safety Breakpoints" for specific nodes?**
   - *What we know:* We can use `interrupt()` inside a node.
   - *What's unclear:* The best way to identify *which* specific advice needs a breakpoint.
   - *Recommendation:* Add a `requires_confirmation` flag to the `Analyst` agent's output schema when recommending specific trades.

2. **Latency of Portfolio Injection**
   - *What we know:* Fetching a summary involves DB queries and YFinance calls.
   - *What's unclear:* Impact on "Time to First Token" if fetched on every request.
   - *Recommendation:* Fetch portfolio summary *once* at the start of the FastAPI endpoint and pass it into the graph as initial state.

## Sources

### Primary (HIGH confidence)
- LangChain Documentation: `astream_events` v2 reference.
- LangGraph Documentation: Persistence and Human-in-the-Loop patterns.
- FastAPI Documentation: `StreamingResponse` and disconnect handling.

### Secondary (MEDIUM confidence)
- LangChain "Open Canvas" repo: Auto-titling background task pattern.
- Community Repo: `agent-service-toolkit` for FastAPI + LangGraph integration.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries are mature and well-documented.
- Architecture: HIGH - SSE and LangGraph patterns are well-vetted.
- Pitfalls: MEDIUM - Based on common developer issues in 2024 ecosystem.

**Research date:** 2026-03-02
**Valid until:** 2026-06-01
