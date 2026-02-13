# Codebase Structure

**Analysis Date:** 2025-03-05

## Directory Layout

```
StockPlanner/
├── src/
│   ├── agents/         # Agent orchestration and state
│   │   ├── nodes/      # Individual graph nodes
│   │   │   ├── analyst/ # Analysis node logic & prompts
│   │   │   └── research/ # Research node logic & utils
│   │   ├── graph.py    # LangGraph definition
│   │   └── state.py    # Agent state definition
│   ├── database/       # Persistence layer
│   │   ├── crud.py     # Database operations
│   │   ├── database.py # SQLAlchemy setup
│   │   └── models.py   # SQL models
│   └── web/            # Presentation layer
│       └── app.py      # Streamlit application
├── tests/              # Test suite
│   ├── test_analyst_node.py
│   ├── test_research_node.py
│   └── test_crud.py
├── stocks.db           # SQLite database file (ignored in git usually)
├── requirements.txt    # Project dependencies
└── pytest.ini          # Test configuration
```

## Directory Purposes

**src/agents/:**
- Purpose: Orchestration of the AI agent workflow.
- Contains: Workflow definitions, state schemas, and node implementations.
- Key files: `graph.py`, `state.py`.

**src/agents/nodes/:**
- Purpose: Modular units of work for the agent.
- Contains: Node functions and domain-specific prompts or utilities.
- Key files: `research/node.py`, `analyst/node.py`.

**src/database/:**
- Purpose: Data persistence and management.
- Contains: ORM models and CRUD utility functions.
- Key files: `models.py`, `crud.py`, `database.py`.

**src/web/:**
- Purpose: Frontend interface.
- Contains: Streamlit UI code.
- Key files: `app.py`.

**tests/:**
- Purpose: Quality assurance.
- Contains: Unit and integration tests for nodes and database logic.
- Key files: `test_analyst_node.py`, `test_crud.py`.

## Key File Locations

**Entry Points:**
- `src/web/app.py`: Main entry point for the user interface.
- `src/agents/graph.py`: Central definition of the agentic process.

**Configuration:**
- `.env`: Environment variables (API keys, etc.) - *Not committed*.
- `requirements.txt`: Python package dependencies.
- `pytest.ini`: Testing configuration.

**Core Logic:**
- `src/agents/nodes/research/node.py`: Data gathering logic.
- `src/agents/nodes/analyst/node.py`: LLM reasoning and reporting logic.
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
- Functions: snake_case (e.g., `research_node`, `create_graph`).

## Where to Add New Code

**New Feature (e.g., technical indicators):**
- Primary code: `src/agents/nodes/research/utils.py` (if shared) or a new node in `src/agents/nodes/`.
- Integration: Update `AgentState` in `src/agents/state.py` and `graph.py`.
- Tests: `tests/test_research_utils.py` or new test file.

**New Agent Node:**
- Implementation: Create a directory in `src/agents/nodes/[node_name]/` with `node.py` and `prompts.py`.
- Integration: Register in `src/agents/graph.py`.

**New Database Model:**
- Implementation: `src/database/models.py`.
- CRUD logic: `src/database/crud.py`.

**Utilities:**
- Shared helpers: `src/agents/nodes/research/utils.py` for market data or a new `src/utils/` if truly cross-cutting.

## Special Directories

**tests/__pycache__/:**
- Purpose: Compiled python files.
- Generated: Yes.
- Committed: No.

**.venv/:**
- Purpose: Virtual environment.
- Generated: Yes.
- Committed: No.

---

*Structure analysis: 2025-03-05*
