# Codebase Structure

**Analysis Date:** 2025-03-05

## Directory Layout

```
StockPlanner/
├── src/
│   ├── agents/             # Multi-agent implementations
│   │   ├── analyst/        # Market analysis logic
│   │   ├── off_topic/      # Handling non-market queries
│   │   ├── research/       # Data gathering logic
│   │   ├── summarizer/     # Final report generation
│   │   └── supervisor/     # Orchestration logic
│   ├── database/           # SQLite/SQLAlchemy layer
│   ├── tools/              # External data tools
│   ├── utils/              # Shared helper functions
│   ├── app.py              # Streamlit entry point
│   ├── graph.py            # LangGraph definition
│   └── state.py            # LangGraph state schema
├── tests/                  # Pytest test suite
├── implementation_plan.md  # Project roadmap
├── pytest.ini              # Test configuration
├── requirements.txt        # Python dependencies
└── stocks.db               # SQLite database (local)
```

## Directory Purposes

**src/agents/:**
- Purpose: Contains the logic for the different AI agents in the system.
- Contains: Sub-directories for each agent, following a consistent structure (`agent.py`, `prompts.py`, `next_agents.py`).
- Key files: `src/agents/base.py` (shared base classes), `src/agents/utils.py` (agent-specific helpers).

**src/database/:**
- Purpose: Handles all persistence logic for the application.
- Contains: DB connection setup, SQLAlchemy models, and CRUD operations.
- Key files: `src/database/database.py`, `src/database/models.py`, `src/database/crud.py`.

**src/tools/:**
- Purpose: Shared utility functions for agents to interact with the outside world.
- Contains: Functions for fetching news and financial data.
- Key files: `src/tools/news.py`, `src/tools/research.py`.

**src/utils/:**
- Purpose: Low-level utility functions.
- Contains: Prompt conversion, tool call formatting, and news cleaning logic.
- Key files: `src/utils/prompt.py`, `src/utils/tool_call.py`.

**tests/:**
- Purpose: Automated testing of agents, tools, and database logic.
- Contains: Pytest files for individual components.
- Key files: `tests/test_supervisor_agent.py`, `tests/test_research_tools.py`.

## Key File Locations

**Entry Points:**
- `src/app.py`: The main Streamlit application.
- `src/graph.py`: The core LangGraph workflow definition.

**Configuration:**
- `pytest.ini`: Configures pytest behavior and pathing.
- `.env`: (Not committed) Contains API keys and secrets.

**Core Logic:**
- `src/state.py`: Defines the `AgentState` which is the central data structure.
- `src/agents/supervisor/agent.py`: The "brain" of the multi-agent system.

**Testing:**
- `tests/`: Directory containing all test files.

## Naming Conventions

**Files:**
- snake_case: `agent_interactions.py`, `research_plan.py`.

**Directories:**
- snake_case: `off_topic`, `summarizer`.

**Functions:**
- snake_case: `create_graph()`, `run_agent_graph()`.

**Classes:**
- PascalCase: `AgentState`, `ResearchPlan`, `BaseAgentResponse`.

## Where to Add New Code

**New Agent:**
1. Create a new directory in `src/agents/`.
2. Implement `agent.py`, `prompts.py`, and `next_agents.py`.
3. Add the new node and edges to `src/graph.py`.
4. Update `AgentInteraction` in `src/state.py` if specific metadata is needed.

**New Tool:**
1. Add the tool function to `src/tools/`.
2. Export it in the relevant agent's `agent.py` by adding it to their `TOOLS_LIST`.

**New Database Model:**
1. Define the model in `src/database/models.py`.
2. Add corresponding CRUD operations in `src/database/crud.py`.

**Utilities:**
- General helpers go in `src/utils/`.
- Agent-specific shared logic goes in `src/agents/utils.py`.

## Special Directories

**src/agents/__pycache__/:**
- Purpose: Compiled Python files.
- Generated: Yes.
- Committed: No.

**.venv/:**
- Purpose: Python virtual environment.
- Generated: Yes.
- Committed: No.

---

*Structure analysis: 2025-03-05*
