---
phase: phase-7
plan: 7-02
type: execute
wave: 1
depends_on: []
files_modified:
  - src/graph/utils/agents.py
  - src/graph/agents/base.py
  - src/graph/agents/research/research_plan.py
  - src/graph/agents/off_topic/off_topic_answer.py
  - src/graph/agents/supervisor/response.py
  - tests/test_analyst_agent.py
  - tests/test_crud.py
  - tests/test_research_tools.py
  - tests/test_supervisor_agent.py
autonomous: true
requirements: [Audit]
---

<objective>
Standardize agent logging and remove legacy artifacts and classes to flatten the architecture.

Purpose: Improve observability and maintainability by removing unnecessary abstraction layers and dead code.
Output: Simplified agent inheritance and a high-fidelity logging system.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/phase-7/7-CONTEXT.md
@.planning/phases/phase-7/7-RESEARCH.md
@src/graph/utils/agents.py
@src/graph/agents/base.py
@src/graph/agents/research/research_plan.py
@src/graph/agents/off_topic/off_topic_answer.py
@src/graph/agents/supervisor/response.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Flatten Agent Schemas and Remove BaseAgentResponse</name>
  <files>
    - src/graph/agents/research/research_plan.py
    - src/graph/agents/off_topic/off_topic_answer.py
    - src/graph/agents/supervisor/response.py
    - src/graph/agents/base.py
  </files>
  <action>
    - For each agent schema (`ResearchPlan`, `OffTopicAnswer`, `SupervisorResponse`):
      - Remove inheritance from `BaseAgentResponse`.
      - Inherit directly from `pydantic.BaseModel`.
      - Explicitly add the `next_agent` field: `next_agent: str = Field(description="The next specialized agent to call")`.
    - Delete `src/graph/agents/base.py`.
  </action>
  <verify>
    Ensure agents still work and schemas are valid.
    Verify `src/graph/agents/base.py` no longer exists.
  </verify>
  <done>
    Legacy "Base Agent" abstraction is removed.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement Standardized Agent Logging Decorator</name>
  <files>src/graph/utils/agents.py</files>
  <action>
    - Refactor `with_logging` decorator:
      - Use `logging.getLogger(__name__)`.
      - In `async_wrapper`, extract `thread_id` from `config["configurable"]`.
      - Generate or extract a `request_id` (default to "N/A" if not found in state/config).
      - Follow the format: `[AGENT_NAME] [Thread: thread_id] [Request: request_id] {message}`.
      - Log starting, completion, and any errors.
      - Stop using `print()` for agent lifecycle logs.
  </action>
  <verify>
    Inspect logs during a mock agent call to ensure the format matches `[AGENT_NAME] [Thread: thread_id] [Request: request_id]`.
  </verify>
  <done>
    Agent nodes now produce high-fidelity, standardized logs.
  </done>
</task>

<task type="auto">
  <name>Task 3: Remove Legacy Tests and Code</name>
  <files>
    - tests/test_analyst_agent.py
    - tests/test_crud.py
    - tests/test_research_tools.py
    - tests/test_supervisor_agent.py
  </files>
  <action>
    - Delete the specified legacy test files that point to outdated paths or modules.
    - Search for any other files in `tests/` that reference `src.agents` or `src.tools` and update or remove them.
  </action>
  <verify>
    `ls tests/test_analyst_agent.py` should fail.
    `pytest tests/` should not fail due to missing modules or outdated paths.
  </verify>
  <done>
    Technical debt in the test suite is reduced.
  </done>
</task>

</tasks>

<verification>
- `BaseAgentResponse` is gone; agents are flat.
- Logs include `thread_id` and `request_id`.
- Obsolete tests are removed.
</verification>

<success_criteria>
- File `src/graph/agents/base.py` is deleted.
- All agent nodes use the standardized logging decorator.
- Legacy tests are gone.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-7/phase-7-02-SUMMARY.md`
</output>
