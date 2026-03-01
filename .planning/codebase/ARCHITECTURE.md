# Architecture

**Analysis Date:** 2025-03-05

## Pattern Overview

**Overall:** Multi-agent Orchestration using LangGraph.

**Key Characteristics:**
- **State-Driven Workflow:** Uses a shared `AgentState` object to pass data between nodes in a directed graph.
- **Supervisor Orchestration:** A central `supervisor` agent determines the routing and delegates tasks to specialized agents.
- **Mesh Routing:** Agents can route directly to other agents or back to the supervisor, allowing for complex multi-turn reasoning.
- **Structured Agent Responses:** Agents return structured interactions that include their findings and the next destination in the graph.

## Layers

**UI/Application Layer:**
- Purpose: Provides a web interface for portfolio management and AI interaction.
- Location: `src/app.py`
- Contains: Streamlit components, state management for the UI, and the entry point for triggering the agent graph.
- Depends on: `src/graph.py`, `src/database/`

**Orchestration Layer:**
- Purpose: Defines the flow of control and data between agents.
- Location: `src/graph.py`, `src/state.py`
- Contains: LangGraph `StateGraph` definition, `AgentState` schema, and routing logic.
- Depends on: `src/agents/`

**Agent Layer:**
- Purpose: Contains specialized logic for different tasks (research, analysis, summarization).
- Location: `src/agents/`
- Contains: Agent implementations, prompts, and local state management for structured outputs.
- Depends on: `src/tools/`, `src/utils/`

**Tool Layer:**
- Purpose: Provides external data access and processing capabilities.
- Location: `src/tools/`
- Contains: News scrapers, financial data fetchers, and search tools.
- Depends on: External APIs (OpenAI, NewsAPI, etc.), `src/utils/`

**Data Layer:**
- Purpose: Handles persistence of portfolio data and caching.
- Location: `src/database/`
- Contains: SQLAlchemy models, CRUD operations, and database initialization.
- Depends on: `src/utils/`

## Data Flow

**Standard Analysis Flow:**

1. **User Input:** User triggers analysis or asks a question via `src/app.py`.
2. **State Initialization:** `run_agent_graph` creates an initial `AgentState` with user holdings and input.
3. **Supervisor Node:** The graph starts at the `supervisor` node (`src/agents/supervisor/agent.py`), which analyzes the request and routes to a specialized agent (e.g., `research`).
4. **Specialized Agent Execution:** The selected agent executes its logic, often calling tools from `src/tools/`.
5. **Mesh Routing:** The agent determines the next step (e.g., routing to `analyst` or back to `supervisor`).
6. **Summarization:** When the task is complete, the flow moves to the `summarizer` agent (`src/agents/summarizer/agent.py`) to produce the final output.
7. **UI Update:** `src/app.py` streams the updates from the graph and displays the final report to the user.

**State Management:**
- Handled by `src/state.py`.
- `AgentState` uses `Annotated[List[AgentInteraction], operator.add]` to maintain a history of all agent activities.
- `session_context` tracks chat history and metadata.

## Key Abstractions

**AgentState:**
- Purpose: The shared memory of the entire graph.
- Examples: `src/state.py`
- Pattern: TypedDict with LangGraph annotations.

**AgentInteraction:**
- Purpose: Represents a single unit of work performed by an agent.
- Examples: `src/state.py`
- Pattern: TypedDict for structured logging and routing.

**BaseAgentResponse:**
- Purpose: Base class for structured LLM outputs to ensure routing information is always present.
- Examples: `src/agents/base.py`
- Pattern: Pydantic Model.

## Entry Points

**Streamlit Web App:**
- Location: `src/app.py`
- Triggers: User interaction via the browser.
- Responsibilities: Initializing the database, managing the UI state, and invoking the agent graph.

**LangGraph Workflow:**
- Location: `src/graph.py`
- Triggers: Called by `run_agent_graph` in `src/app.py`.
- Responsibilities: Compiling and executing the agent state machine.

## Error Handling

**Strategy:** Resilience through status updates and fallback routing.

**Patterns:**
- **Try-Except Blocks:** Used around graph execution in `src/app.py` to capture and display errors in the UI.
- **Default Routing:** The `create_mesh_router` in `src/graph.py` includes fallbacks to the `summarizer` if an invalid `next_agent` is specified.
- **Tool Level Resilience:** Individual tools in `src/agents/research/agent.py` are executed in a thread pool with error trapping to prevent a single tool failure from crashing the agent.

## Cross-Cutting Concerns

**Logging:** Handled by a `@with_logging` decorator in `src/agents/utils.py`.
**Validation:** Pydantic is used for structured LLM outputs and model definitions.
**Authentication:** Environment variables loaded via `dotenv`, managed in `src/app.py`.

---

*Architecture analysis: 2025-03-05*
