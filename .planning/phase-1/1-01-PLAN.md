---
phase: phase-1
plan: 1-01
type: execute
wave: 1
depends_on: []
files_modified: [requirements.txt, .env.template, src/graph/, src/services/]
autonomous: true
requirements: [REQ-020, REQ-030]
user_setup:
  - service: Railway
    why: "Database connection for PostgreSQL"
    env_vars:
      - name: DATABASE_URL
        source: "Railway Dashboard -> PostgreSQL -> Connect -> Connection URL (Internal for production, Public for local)"

must_haves:
  truths:
    - "Directory structure follows 1-CONTEXT.md (src/graph/ exists)"
    - "Project imports are consistent and non-breaking"
  artifacts:
    - path: "src/graph/graph.py"
      provides: "Agentic orchestration entry point"
    - path: "requirements.txt"
      provides: "List of all project dependencies including asyncpg and asgi-correlation-id"
    - path: ".env.template"
      provides: "Blueprint for environment variables"
  key_links:
    - from: "src/graph/"
      to: "src.graph"
      via: "Refactored absolute imports"
      pattern: "from src\\.graph"
---

<objective>
Align project directory structure with the latest architecture decisions and setup foundational configuration files.

Purpose: Ensure a clean, feature-based organization that supports the API-first architecture.
Output: Reorganized code and dependency list.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phase-1/1-CONTEXT.md
@.planning/phase-1/1-RESEARCH.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Project Reorganization</name>
  <files>src/graph/, src/services/, src/database/crud.py</files>
  <action>
    1. Create the new directory structure: `mkdir -p src/graph/ src/api/controllers/ src/api/schemas/ src/services/`.
    2. Move existing graph-related components:
       - Move `src/agents/`, `src/tools/`, and `src/utils/` into `src/graph/`.
       - Move `src/graph.py` to `src/graph/graph.py`.
       - Move `src/state.py` to `src/graph/state.py`.
    3. Move business logic:
       - Move `src/database/crud.py` to `src/services/portfolio.py` (since it contains investment calculation logic).
    4. Update all imports globally to reflect the new structure:
       - `from src.agents` -> `from src.graph.agents`
       - `from src.tools` -> `from src.graph.tools`
       - `from src.utils` -> `from src.graph.utils`
       - `from src.graph` (where applicable) -> `from src.graph.graph`
       - `from src.state` -> `from src.graph.state`
       - `from src.database.crud` -> `from src.services.portfolio`
    5. Clean up empty directories if any.
  </action>
  <verify>Run `find src -name "*.py" | xargs grep "from src."` to ensure all imports are correctly prefixed with the new paths.</verify>
  <done>Codebase reorganized without broken imports.</done>
</task>

<task type="auto">
  <name>Task 2: Dependencies & Environment</name>
  <files>requirements.txt, .env.template</files>
  <action>
    1. Update `requirements.txt` with the standard stack from 1-RESEARCH.md:
       - `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0.0`, `asyncpg`, `pydantic-settings`, `asgi-correlation-id`, `python-dotenv`, `httpx`, `langchain-core`, `langgraph`.
    2. Create `.env.template` including:
       - `DATABASE_URL` (PostgreSQL async URL placeholder: `postgresql+asyncpg://...`)
       - `PORT` (default 8000)
       - `LOG_LEVEL` (default INFO)
       - `ENVIRONMENT` (default development)
       - `OPENAI_API_KEY` (placeholder)
  </action>
  <verify>Check `requirements.txt` for all required libraries and verify `.env.template` has all placeholders.</verify>
  <done>Dependencies and environment templates are ready.</done>
</task>

</tasks>

<verification>
Validate the directory structure with `ls -R src/` and check for any syntax errors in moved files using `python -m compileall src/`.
</verification>

<success_criteria>

- Project structure matches `1-CONTEXT.md` exactly.
- All dependencies are listed in `requirements.txt`.
- No broken imports in the reorganized codebase.
  </success_criteria>

<output>
After completion, create `.planning/phases/phase-1/phase-1-1-01-SUMMARY.md`
</output>
