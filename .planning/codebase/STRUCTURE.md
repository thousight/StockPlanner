# Codebase Structure

**Analysis Date:** 2025-03-05

## Directory Layout

```
StockPlanner/
├── src/
│   ├── agents/         # Agent orchestration and implementations
│   │   ├── analyst/    # Analysis agent package
│   │   ├── cache_maintenance/ # Cache agent package
│   │   ├── research/   # Research agent package
│   │   ├── supervisor/ # Supervisor agent package
│   │   └── agents.py   # General agent definitions/references
│   ├── database/       # Persistence layer
│   │   ├── crud.py     # Database operations
│   │   ├── database.py # SQLAlchemy setup
│   │   └── models.py   # SQL models
│   ├── tools/          # Global tools referenced by agents
│   │   ├── news.py     # News fetching tools
│   │   └── research.py # Financial data tools
│   ├── utils/          # Shared utilities
│   │   ├── news.py     # Internal helpers for news
│   │   └── prompt.py   # Prompt formatting utilities
│   ├── app.py          # Streamlit application
│   ├── graph.py        # LangGraph workflow definition
│   └── state.py        # Agent state definition
├── tests/              # Test suite
│   ├── test_analyst_agent.py
│   ├── test_crud.py
│   ├── test_research_tools.py
│   └── test_supervisor_agent.py
├── stocks.db           # SQLite database file (ignored in git usually)
├── requirements.txt    # Project dependencies
└── pytest.ini          # Test configuration
```

## Directory Purposes

**src/agents/:**

- Purpose: Orchestration of the AI agent workflow and agent implementations.
- Contains: Individual agent packages with their prompts and logic.
- **Strict Format:** Each agent MUST have its own directory containing at least `agent.py` (logic) and `prompts.py` (LLM templates).
- Key files: `research/agent.py`, `analyst/agent.py`.

**src/tools/:**

- Purpose: Reusable tool definitions that are accessed by agents.
- Contains: Functions configured as structured tools.
- Key files: `news.py`, `research.py`.

**src/utils/:**

- Purpose: Core helper logic serving deeper internal layers.
- Contains: Formatters and parsing tools.
- Key files: `news.py`, `prompt.py`.

**src/database/:**

- Purpose: Data persistence and management.
- Contains: ORM models and CRUD utility functions.
- Key files: `models.py`, `crud.py`, `database.py`.

**src/app.py:**

- Purpose: Frontend interface.
- Contains: Streamlit UI code.

**tests/:**

- Purpose: Quality assurance.
- Contains: Unit tests for agents, tools, and database logic.
- Key files: `test_analyst_agent.py`, `test_crud.py`.

## Key File Locations

**Entry Points:**

- `src/app.py`: Main entry point for the user interface.
- `src/graph.py`: Central definition of the agentic process.

**Configuration:**

- `.env`: Environment variables (API keys, etc.) - _Not committed_.
- `requirements.txt`: Python package dependencies.
- `pytest.ini`: Testing configuration.

**Core Logic:**

- `src/agents/research/agent.py`: Data gathering workflow step.
- `src/agents/analyst/agent.py`: LLM reasoning and reporting workflow step.
- `src/database/crud.py`: All database write/read logic.

**Testing:**

- `tests/`: Directory containing all test modules.

## Naming Conventions

**Files:**

- Snake case: `app.py`, `models.py`, `test_crud.py`.

**Directories:**

- Snake case: `nodes`, `research`, `analyst`.

**Classes/Functions:**

- Classes: PascalCase (e.g., `Stock`, `AgentState`).
- Functions: snake_case (e.g., `research_agent`, `create_graph`).

## Where to Add New Code

**New Feature (e.g., technical indicators):**

- Primary code: `src/tools/research.py` (if shared tool) or a new domain tool.
- Integration: Update `AgentState` in `src/state.py` and `src/graph.py`.
- Tests: `tests/test_research_tools.py` or new test file.

**New Agent:**

- Implementation: Create a directory in `src/agents/[agent_name]/` with `agent.py` and `prompts.py`.
- Integration: Register the new valid transition in `src/graph.py` and `src/agents/supervisor/agent.py`.

**New Database Model:**

- Implementation: `src/database/models.py`.
- CRUD logic: `src/database/crud.py`.

**Utilities:**

- Shared wrappers and formatting logic: `src/utils/` modules.

## Special Directories

**tests/**pycache**/:**

- Purpose: Compiled python files.
- Generated: Yes.
- Committed: No.

**.venv/:**

- Purpose: Virtual environment.
- Generated: Yes.
- Committed: No.

---

_Structure analysis: 2025-03-05_
