# Phase 23 Context: Execution Tooling & Feedback

## Phase Goal
Integrate the `CodeGeneratorAgent` into the main LangGraph workflow and implement the cross-agent feedback loop for quantitative analysis.

## Key Decisions

### 1. Routing & Specialization
- **Agent Name:** **Quantitative Researcher** (Code: `code_generator`).
- **Supervisor Logic:** Uses intuitive LLM routing to identify math/calculation tasks. Prefer existing API tools for raw metrics; use `code_generator` for manipulation or complex synthesis.
- **Handoffs:** Standard research agents (e.g., Fundamental, Macro) can specify `code_generator` as their `next_agent` if a custom calculation is required.

### 2. Graph Architecture & Flow
- **Parallel Execution:** `code_generator` runs in parallel with other research nodes to maximize efficiency.
- **Dynamic Input:** The agent has access to `user_context` (portfolio) and any `market_context` or prior `agent_interactions` currently in the state.
- **Analyst Format:** Output is wrapped in `<calculation_result>` tags to distinguish "Hard Numbers" from general "Research Observations".

### 3. Inter-Agent Feedback Loop
- **Correction Route:** A **Direct Edge** connects `analyst` -> `code_generator`.
- **Trigger:** Analyst can request a re-run if quantitative results are logically inconsistent or insufficient for the final analysis.
- **Feedback Type:** **Specific Feedback**. Analyst provides a detailed instruction on what logic to fix (e.g., "The volatility calculation forgot to annualize; please fix.").
- **Recursion Guard:** Max **2 re-runs** triggered by the Analyst. Total attempts (including internal agent retries) are tracked.
- **Persistence:** If calculations fail after all retries, the Analyst notes the data gap and explains the failure in the final output.

## Code Context & Integration
- **Graph Modification:** Update `create_graph` in `src/graph/graph.py` to include the `code_generator` node and the feedback edge.
- **Supervisor Update:** Refine `src/graph/agents/supervisor/agent.py` to recognize and route to the new specialist.
- **Analyst Update:** Modify `src/graph/agents/analyst/agent.py` to handle the new feedback logic and tagged result parsing.

## Next Steps
1.  **Phase 23 Research:** Verify LangGraph's support for direct edges between functional nodes (non-supervisor) and state preservation during loops.
2.  **Phase 23 Plan:** Draft the graph changes and the Analyst's feedback logic.
