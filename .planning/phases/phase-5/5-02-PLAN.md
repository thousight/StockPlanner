---
phase: 05-agentic-flow-refinement
plan: 5-02
type: execute
wave: 2
depends_on: [5-01]
files_modified: [requirements.txt, src/services/complexity.py, src/graph/state.py, src/graph/agents/summarizer/agent.py]
autonomous: true
requirements: [REQ-011]
---

<objective>
Implement complexity analysis and automated metadata generation for reports.
Purpose: Enable conditional interrupts based on content depth and categorize syntheses automatically.
Output: Complexity scoring service and enhanced summarizer agent.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-5/5-CONTEXT.md
@src/graph/state.py
@src/graph/agents/summarizer/agent.py
@requirements.txt
</context>

<tasks>

<task type="auto">
  <name>Task 1: Complexity Scoring Service</name>
  <files>requirements.txt, src/services/complexity.py</files>
  <action>
    - Add `textstat` to `requirements.txt`.
    - Create `src/services/complexity.py`.
    - Implement `evaluate_complexity(text: str) -> float`:
      - P1: Use `textstat.flesch_reading_ease` or similar linguistic metrics.
      - P0: Check for Action Keywords (BUY, SELL, TRADE, INVEST). If present, return high score (force interrupt).
      - Return a normalized score or a boolean `requires_interrupt`.
  </action>
  <verify>Run a unit test for `evaluate_complexity` with short vs long text and action keywords.</verify>
  <done>Complexity scoring logic accurately identifies action keywords and measures text depth.</done>
</task>

<task type="auto">
  <name>Task 2: Enhanced Metadata Generation</name>
  <files>src/graph/state.py, src/graph/agents/summarizer/agent.py</files>
  <action>
    - Update `AgentState`'s `pending_report` TypedDict to include: `title`, `category`, `topic`, `tags`, `complexity_score`.
    - Update `summarizer_agent` in `src/graph/agents/summarizer/agent.py`:
      - Extract or generate Title, Category, Topic, and Tags from the interaction history or LLM response.
      - Calculate `complexity_score` using `ComplexityService`.
      - Populate `pending_report` in the state.
  </action>
  <verify>Check graph logs during execution to ensure `pending_report` contains all metadata fields.</verify>
  <done>Summarizer agent produces enriched metadata and complexity scores for every report.</done>
</task>

</tasks>

<verification>
Verify that reports now have titles, categories, and tags, and that complexity scores are calculated.
</verification>

<success_criteria>
- `textstat` is integrated.
- Reports contain automated Title, Category, Topic, and Tags.
- Complexity scoring correctly identifies reports needing human oversight.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-5/5-02-SUMMARY.md`
</output>
