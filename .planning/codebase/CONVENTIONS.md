# Coding Conventions

**Analysis Date:** 2025-02-14

## Naming Patterns

**Files:**
- snake_case for all Python files.
- Example: `src/graph.py`, `src/database/crud.py`
- Test files prefixed with `test_`. Example: `tests/test_crud.py`

**Functions:**
- snake_case for all functions.
- Example: `research_agent`, `add_stock`, `resolve_symbol`
- Private helper functions prefixed with underscore. Example: `_parse_yf_news_item`

**Variables:**
- snake_case for local variables and parameters.
- Example: `holdings`, `research_data`, `db_session`

**Types:**
- PascalCase for classes (models, state, tests).
- Example: `Stock`, `Transaction`, `AgentState`, `TestResearchNode`

## Code Style

**Formatting:**
- Standard PEP 8 alignment observed.
- No explicit formatting tool (like Black) config found, but code is consistently formatted with 4-space indentation.

**Linting:**
- Not explicitly configured via `.flake8` or `pyproject.toml`.
- Type hints are used for function parameters and return types where possible.

## Import Organization

**Order:**
1. Standard library imports (e.g., `from typing import Dict`).
2. Third-party library imports (e.g., `import yfinance as yf`).
3. Local application imports (e.g., `from src.database.models import Stock`).

**Path Aliases:**
- Absolute imports starting from `src` are preferred.
- Example: `from src.agents.state import AgentState`

## Error Handling

**Patterns:**
- Try-except blocks used in utility functions to handle external API failures (yfinance, DuckDuckGo).
- Returns default empty values (e.g., `[]`, `{}`, `0`, `None`) on failure to ensure system stability.
- Example: `src/tools/research.py (or src/tools/news.py)` handles exceptions in `resolve_symbol` by returning a default dictionary.

## Logging

**Framework:** `print` statements.

**Patterns:**
- DEBUG and Error messages are printed to stdout/stderr.
- Example: `print(f"Error fetching news for {stock.ticker}: {e}")`

## Comments

**When to Comment:**
- Inline comments used for complex logic (e.g., cost basis calculation in `src/database/crud.py`).
- TODOs (if any) are used for future improvements.

**JSDoc/TSDoc:**
- Python triple-quoted docstrings used for function and class documentation.
- Example:
  ```python
  def resolve_symbol(symbol: str) -> Dict[str, Any]:
      """
      Resolve the symbol to its data: price, change, news, info.
      """
  ```

## Function Design

**Size:**
- Functions are generally kept small and focused on a single responsibility.
- Large tasks are broken down using `ThreadPoolExecutor` and helper functions.

**Parameters:**
- Explicit typing used for parameters where clarity is needed.
- Example: `db: Session`, `symbol: str`.

**Return Values:**
- Return types are occasionally hinted using `->`.
- Consistent return structures (e.g., always returning a dict or a list) are used in research utilities.

## Module Structure for Agents

**Architecture:**
- Each agent agent MUST be organized as a directory-based package.
- **Node Logic:** The primary logic for the agent agent (the function integrated into the graph) MUST reside in `agent.py`.
- **Prompts:** All LLM prompts, system messages, and template strings MUST reside in `prompts.py`.
- **Structure:**
  ```text
  src/agents/<agent_name>/
  ├── agent.py
  └── prompts.py
  ```
- **Rationale:** Separating prompts from logic improves readability and allows for easier prompt engineering without touching the execution flow.

## Module Design

**Exports:**
- Modules export functions and classes directly.

---

*Convention analysis: 2025-02-14*
