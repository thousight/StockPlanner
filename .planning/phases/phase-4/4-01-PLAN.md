---
phase: phase-4
plan: 01
type: execute
wave: 1
depends_on: []
files_modified: [src/graph/state.py, src/services/context_injection.py, src/graph/graph.py, src/graph/utils/prompt.py]
autonomous: true
requirements: [REQ-011, REQ-012]
must_haves:
  truths:
    - "AgentState includes a structured field for injected portfolio summary"
    - "Portfolio summary is formatted as a concise text block for LLM consumption"
    - "The graph uses AsyncPostgresSaver for persistent state tracking"
  artifacts:
    - path: "src/services/context_injection.py"
      provides: "LLM-ready portfolio summary generation"
    - path: "src/graph/graph.py"
      provides: "Compiled graph with checkpointer integration"
  key_links:
    - from: "src/services/context_injection.py"
      to: "src/services/portfolio.py"
      via: "get_portfolio_summary call"
---

<objective>
Establish the foundational orchestration for the agentic graph, including persistence integration and automated portfolio context injection. This ensures the graph can maintain state across requests and starts every conversation with a clear understanding of the user's financial status.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@src/graph/state.py
@src/graph/graph.py
@src/services/portfolio.py
@src/graph/persistence.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update AgentState and Prompt Utilities</name>
  <files>src/graph/state.py, src/graph/utils/prompt.py</files>
  <action>
    - Update `UserContext` in `src/graph/state.py` to include `portfolio_summary: str` and `user_id: str`.
    - Update `src/graph/utils/prompt.py` to include the `portfolio_summary` in the `convert_state_to_prompt` output so agents can see the injected context.
  </action>
  <verify>Check `src/graph/state.py` for new fields. Run a small script to verify `convert_state_to_prompt` includes the new fields in its output.</verify>
  <done>AgentState supports portfolio context and prompt utilities expose it to the LLM.</done>
</task>

<task type="auto">
  <name>Task 2: Implement Portfolio Context Injection Service</name>
  <files>src/services/context_injection.py</files>
  <action>
    - Create `src/services/context_injection.py`.
    - Implement `format_portfolio_for_llm(summary: PortfolioSummary) -> str` as defined in RESEARCH.md.
    - Implement `get_user_context_data(db: Session, user_id: str) -> Dict` that fetches the portfolio summary using `get_portfolio_summary` and formats it.
  </action>
  <verify>Create a unit test or script that calls `get_user_context_data` for a test user and verifies the returned string contains key portfolio metrics (Value, Gain/Loss, Sectors).</verify>
  <done>Service exists to transform raw database portfolio data into an LLM-ready context block.</done>
</task>

<task type="auto">
  <name>Task 3: Compile Graph with Persistence</name>
  <files>src/graph/graph.py</files>
  <action>
    - Modify `create_graph()` in `src/graph/graph.py` to accept an optional `checkpointer` argument.
    - Update `workflow.compile(checkpointer=checkpointer)` to enable persistence.
    - Ensure all nodes (Supervisor, Research, etc.) are imported correctly.
  </action>
  <verify>Run a script that initializes the graph with a mock `AsyncPostgresSaver` (or `MemorySaver` for testing) and verifies `graph.get_state` returns the expected structure.</verify>
  <done>LangGraph is configured to use the PostgreSQL checkpointer for thread persistence.</done>
</task>

</tasks>

<verification>
Verify that the graph can be instantiated with a checkpointer and that the state structure correctly accommodates the injected portfolio summary.
</verification>

<success_criteria>
- `AgentState` correctly reflects the user's portfolio and ID.
- `src/services/context_injection.py` provides formatted strings for LLM injection.
- `create_graph()` supports `AsyncPostgresSaver` for persistence.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-4/phase-4-01-SUMMARY.md`
</output>
