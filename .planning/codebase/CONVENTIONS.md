# Coding Conventions

**Analysis Date:** 2024-05-22

## Naming Patterns

**Files:**
- `snake_case.py` (e.g., `src/app.py`, `src/agents/analyst/agent.py`)

**Functions:**
- `snake_case()` (e.g., `run_agent_graph()`, `analyst_agent()`)

**Variables:**
- `snake_case` (e.g., `user_input`, `current_datetime`)

**Types/Classes:**
- `PascalCase` (e.g., `Stock`, `Transaction`, `AgentState`, `BaseAgentResponse`)

## Code Style

**Formatting:**
- No explicit formatting tool (like Black or Prettier) detected in configuration.
- Standard Python (PEP 8) style is followed.

**Linting:**
- No explicit linting configuration (like Flake8 or Pylint) detected.

## Import Organization

**Order:**
1. Standard library imports (e.g., `import os`, `import sys`)
2. Third-party library imports (e.g., `import streamlit as st`, `from langchain_core.messages import HumanMessage`)
3. Local module imports (e.g., `from src.database.database import get_db`)

**Path Aliases:**
- Project root is added to `sys.path` in `src/app.py` to allow absolute imports from `src`.

## Error Handling

**Patterns:**
- **Decorators:** `@with_logging` decorator in `src/agents/utils.py` is used to catch, log (print), and re-throw exceptions in agent functions.
- **Try-Except:** Used around critical operations like agent graph execution in `src/app.py`.
- **Traceback:** `traceback.format_exc()` is commonly used to capture detailed error information.

## Logging

**Framework:** `print` statements and `traceback`.

**Patterns:**
- Unified logging for agents via `@with_logging` in `src/agents/utils.py`.
- Prints "--- AGENT_NAME: Starting ---" and logs errors with stack traces.

## Comments

**When to Comment:**
- Section headers in large files like `src/app.py` (e.g., `# --- Main App ---`).
- Explaining complex logic or configurations.

**JSDoc/TSDoc:**
- Triple-quote docstrings (`"""Docstring"""`) are used for class and function documentation.

## Function Design

**Size:**
- Streamlit application logic in `src/app.py` contains large functions (`run_agent_graph`).
- Agent logic is generally modularized into specialized functions.

**Parameters:**
- LangGraph agents consistently take `state: AgentState` and `config: RunnableConfig`.

**Return Values:**
- Agents return a dictionary that updates the `AgentState`.

## Module Design

**Exports:**
- Explicit function and class exports are used across modules.

**Barrel Files:**
- Not extensively used; direct imports from specific modules are preferred.

---

*Convention analysis: 2024-05-22*
