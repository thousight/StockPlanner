---
phase: phase-8
plan: 8-02
type: execute
wave: 2
depends_on: [8-01]
files_modified:
  - tests/unit/agents/test_research_node.py
  - tests/unit/agents/test_supervisor_node.py
  - tests/unit/agents/test_analyst_node.py
  - tests/unit/services/test_titler.py
autonomous: true
requirements:
  - REQ-032
must_haves:
  truths:
    - "Research agent correctly plans tool calls based on user questions."
    - "Supervisor agent routes to the correct specialized agent for different input types."
    - "Analyst agent correctly synthesizes adversarial arguments and handles safety interrupts."
    - "Auto-titling and summarizer metadata (category, tags) are accurate for financial topics."
  artifacts:
    - path: "tests/unit/agents/test_research_node.py"
      provides: "Verification of Research agent tool planning and parallel execution"
    - path: "tests/unit/agents/test_supervisor_node.py"
      provides: "Verification of Supervisor routing logic"
    - path: "tests/unit/agents/test_analyst_node.py"
      provides: "Node-level testing for the debate subgraph and safety interrupts"
    - path: "tests/unit/services/test_titler.py"
      provides: "Comprehensive verification of thread title generation"
  key_links:
    - from: "tests/unit/agents/test_analyst_node.py"
      to: "src/graph/agents/analyst/subgraph.py"
      via: "subgraph invocation with mocked state"
    - from: "tests/unit/agents/test_research_node.py"
      to: "src/graph/tools/"
      via: "execute_tool call verification"
---

<objective>
Implement node-level verification for LangGraph agents using state teleportation, focusing on tool planning, routing accuracy, adversarial debate synthesis, and metadata generation.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-8/8-CONTEXT.md
@.planning/phases/phase-8/8-RESEARCH.md
@src/graph/agents/research/agent.py
@src/graph/agents/supervisor/agent.py
@src/graph/agents/analyst/agent.py
@src/graph/agents/analyst/subgraph.py
@src/graph/agents/summarizer/agent.py
@src/services/titler.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Research Agent Tool Planning Verification</name>
  <files>tests/unit/agents/test_research_node.py</files>
  <action>
    Implement unit tests for the Research agent:
    - Mock `ChatOpenAI` to return a predefined `ResearchPlan`.
    - Verify that `research_agent` correctly parses the plan and calls `execute_tool` for each step.
    - Test `execute_tool` logic: Ensure it correctly handles tool name mapping, argument conversion (especially for `web_search`), and propagation of `user_agent`.
    - Mock actual tools (financials, news, search) to return sample strings and verify the aggregated `answer` in `agent_interactions`.
  </action>
  <verify>
    Run `pytest tests/unit/agents/test_research_node.py`
  </verify>
  <done>
    Research agent tool selection and parallel execution logic is verified.
  </done>
</task>

<task type="auto">
  <name>Task 2: Supervisor Routing & Analyst Debate Verification</name>
  <files>tests/unit/agents/test_supervisor_node.py, tests/unit/agents/test_analyst_node.py</files>
  <action>
    Implement unit tests for Supervisor and Analyst agents:
    - Supervisor: Mock LLM to return `SupervisorResponse` for various inputs (e.g., "Analyze AAPL" -> research, "What is my portfolio gain?" -> analyst/supervisor). Verify routing decision in state.
    - Analyst:
      - Test individual nodes of the debate subgraph (`generator`, `bull`, `bear`, `synthesizer`) by passing mocked `DebateState`.
      - Test `analyst_agent` safety interrupt: Mock `interrupt` and simulate user 'approve' vs 'reject' responses. Verify that the final report is either returned or cancelled based on user input.
  </action>
  <verify>
    Run `pytest tests/unit/agents/test_supervisor_node.py tests/unit/agents/test_analyst_node.py`
  </verify>
  <done>
    Routing decisions and adversarial debate synthesis (including human-in-the-loop interrupts) are verified.
  </done>
</task>

<task type="auto">
  <name>Task 3: Summarizer & Titler Verification</name>
  <files>tests/unit/agents/test_summarizer_node.py, tests/unit/services/test_titler.py</files>
  <action>
    Implement tests for synthesis and metadata generation:
    - Summarizer: Mock LLM to return `SummarizerOutput`. Verify that `summarizer_agent` correctly maps the output to `pending_report` metadata (category, topic, tags) and calculates complexity.
    - Auto-Titling: Test `generate_thread_title` with various message pairs (e.g., "Help with AAPL" -> "Apple Stock Analysis"). Verify the background update task `update_thread_title_background` using a mocked database session.
  </action>
  <verify>
    Run `pytest tests/unit/agents/test_summarizer_node.py tests/unit/services/test_titler.py`
  </verify>
  <done>
    Summarization metadata and thread titling logic are accurate and robust.
  </done>
</task>

</tasks>

<verification>
Run all agent-level unit tests:
`pytest tests/unit/agents/`
</verification>

<success_criteria>
- Agent routing and tool planning are verified for happy paths.
- Analyst debate subgraph nodes are verified individually.
- Safety interrupts in the Analyst agent handle user rejection correctly.
- Auto-titling generates appropriate titles for financial queries.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-8/8-02-SUMMARY.md`
</output>
