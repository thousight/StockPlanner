# Context - Phase 7: Simplification & Cleanup

This document captures implementation decisions for Phase 7 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Redundant Logic Consolidation
- **Agent Constraints:** Agent nodes are strictly prohibited from implementing internal data manipulation logic. They are only allowed to use the **Tools** explicitly imported for them.
- **Market Data Unification:** All logic for fetching market data (primarily `yfinance` calls) must be consolidated into a single, unified service in `src/services/market_data.py`.
- **Agent Architecture:** Agent nodes will remain independent and flat; no shared "Base Agent" class or shared helpers will be implemented in this phase.
- **Financial Math:** All complex financial calculations (e.g., ACB, PNL) will reside strictly within the `src/services/portfolio.py` service.

## 2. Legacy Artifact Removal
- **Dead Code Policy:** Any discovered unused imports, variables, or functions in the `src/` directory must be **removed immediately**.
- **Test Suite Sweep:** The `tests/` directory will be audited to remove any legacy test files that refer to deleted models or outdated directory paths.
- **Preservation:** Root-level logs and backups, as well as `__pycache__` and `.pytest_cache` folders, will be left as is for the system to manage.

## 3. Directory Structure Preservation
- **Structure Logic:** The current directory layout will be maintained:
  - Keep nested agent folders in `src/graph/agents/`.
  - Keep `schemas/` and `controllers/` in the `src/` root (no `api/` grouping).
  - Keep `lifecycle/` as a separate top-level directory in `src/`.
  - Keep `main.py` in the project root for Railway compatibility.

## 4. Error Handling & Logging Standardization
- **Exceptions:** No custom Application Exceptions will be defined; the system will continue to use standard FastAPI `HTTPException` objects.
- **Logging Pattern:** All agent nodes must use a standardized logging prefix: `[AGENT_NAME]`. Every log message must explicitly include the `thread_id` and `request_id` for enhanced observability.
- **Validation:** Continue using default Pydantic validation error messages for the mobile client.
- **Catching Policy:** Error catching and handling will be prioritized at the **Controller layer** only; service functions should avoid broad `try/except` blocks unless necessary for specific resource cleanup.
