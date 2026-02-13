# Architecture

**Analysis Date:** 2025-03-05

## Pattern Overview

**Overall:** Layered Agentic Architecture

**Key Characteristics:**
- **Stateful Agent Workflow:** Uses LangGraph to manage a stateful, directed acyclic graph (DAG) of specialized nodes.
- **Service-Oriented Nodes:** Each node in the graph has a single responsibility (research, analysis, maintenance).
- **Relational Persistence:** Uses SQLAlchemy for structured data storage and history tracking.

## Layers

**Presentation Layer:**
- Purpose: Provides a web-based UI for portfolio management and triggering analysis.
- Location: `src/web/`
- Contains: Streamlit application logic.
- Depends on: `src/database/`, `src/agents/`
- Used by: End user

**Orchestration Layer:**
- Purpose: Defines the execution flow of the AI agents.
- Location: `src/agents/graph.py`
- Contains: LangGraph workflow definition and state management.
- Depends on: `src/agents/state.py`, `src/agents/nodes/`
- Used by: `src/web/app.py`

**Service/Node Layer:**
- Purpose: Implements the specific logic for each step in the agent workflow.
- Location: `src/agents/nodes/`
- Contains: Research logic (data fetching), Analysis logic (LLM reasoning), and maintenance tasks.
- Depends on: `src/agents/state.py`, `langchain`, `src/database/`
- Used by: `src/agents/graph.py`

**Data Access Layer:**
- Purpose: Abstracts database interactions.
- Location: `src/database/`
- Contains: SQLAlchemy models, session management, and CRUD operations.
- Depends on: `sqlalchemy`
- Used by: `src/web/app.py`, `src/agents/nodes/`

## Data Flow

**Portfolio Analysis Flow:**

1. **Trigger:** User clicks "Run Portfolio Analysis" in the Streamlit UI (`src/web/app.py`).
2. **State Initialization:** The UI fetches the current portfolio from the DB via `src/database/crud.py` and initializes the `AgentState`.
3. **Graph Execution:** The UI invokes the compiled LangGraph (`src/agents/graph.py`).
4. **Research Phase:** The `research_node` (`src/agents/nodes/research/node.py`) fetches market news and stock data in parallel using `ThreadPoolExecutor`.
5. **Analysis Phase:** The `analyst_node` (`src/agents/nodes/analyst/node.py`) formats the gathered data and uses `ChatOpenAI` (GPT-4o) to generate an investment report.
6. **Maintenance Phase:** The `cache_maintenance_node` (`src/agents/nodes/nodes.py`) performs cleanup tasks like removing expired news entries.
7. **Result Delivery:** The final state is returned to the UI, which displays the generated `analysis_report`.

**State Management:**
- Handled by `AgentState` (`src/agents/state.py`), a `TypedDict` that stores messages, portfolio data, research results, and the final analysis report.

## Key Abstractions

**AgentState:**
- Purpose: The shared memory/context passed between nodes in the graph.
- Examples: `src/agents/state.py`
- Pattern: TypedDict with LangGraph Annotations.

**Workflow Graph:**
- Purpose: Defines the sequence and logic of agent operations.
- Examples: `src/agents/graph.py`
- Pattern: LangGraph StateGraph.

**SQLAlchemy Models:**
- Purpose: Define the schema for stocks, transactions, and snapshots.
- Examples: `src/database/models.py`
- Pattern: Declarative Base.

## Entry Points

**Streamlit Web App:**
- Location: `src/web/app.py`
- Triggers: Manual user interaction.
- Responsibilities: UI rendering, session state management, DB connection, agent invocation.

**Graph Creator:**
- Location: `src/agents/graph.py`
- Triggers: Called by the UI to instantiate the agent system.
- Responsibilities: Compiling the LangGraph workflow.

## Error Handling

**Strategy:** Localized try-except blocks with fallback responses.

**Patterns:**
- **Node-level Try-Except:** Nodes like `analyst_node` catch LLM exceptions and return an error message in the state rather than crashing the graph.
- **DB Session Management:** `get_db` generator in `src/database/database.py` ensures sessions are closed even if errors occur.

## Cross-Cutting Concerns

**Logging:** Standard output prints for debugging (e.g., in `analyst_node`).
**Validation:** Basic type checking via `TypedDict` in `AgentState`.
**Authentication:** API Key management via environment variables and Streamlit sidebar input.

---

*Architecture analysis: 2025-03-05*
