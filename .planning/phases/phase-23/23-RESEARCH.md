# Phase 23 Research: Execution Tooling & Feedback

## 1. LangGraph Flow Architecture
To implement the `analyst -> code_generator` loop while maintaining the parallel research squad, we will use a combination of **Parallel Fan-out** and **Conditional Loopback**.

### Graph Topology:
1.  **Supervisor Node**: Fan-out to researchers (`fundamental`, `sentiment`, `macro`, `narrative`, `generic`, `code_generator`).
2.  **Synchronization Point**: All researchers (including `code_generator`) point to the **Analyst Node** (Implicit Fan-in).
3.  **Analyst Node**: Processes all findings.
4.  **Correction Router (Conditional Edge)**:
    - If `analyst` requested a correction AND `retry_count < 2`: Route to `code_generator`.
    - Otherwise: Route to `summarizer`.

---

## 2. State Management & Reducers
The existing `AgentState` is well-equipped for this loop:
- `agent_interactions`: Uses `operator.add`. This preserves the history of calculations and previous corrections, allowing the `code_generator` to see its own history for self-correction.
- **New State Field**: We need a `code_revision_count` (int) to track how many times the *Analyst* has sent the task back. This is distinct from the generator's *internal* retries.

---

## 3. Analyst Feedback Mechanism
The `AnalystAgent` needs to be updated to:
1.  Recognize `<calculation_result>` tags.
2.  Check for logical consistency (e.g., "The annualized return is 5000%, this seems wrong").
3.  Output a specific `interaction` with `next_agent: "code_generator"` and a detailed feedback message in the `answer` field if a correction is needed.

---

## 4. Supervisor Routing Logic
The `SupervisorAgent` prompt will be updated to:
- Recognize "quantitative" tasks (math, simulations, custom data grouping).
- Route to `code_generator` either as a standalone researcher or in parallel with others.
- Understand that `code_generator` is the preferred tool for *manipulating* data, while `fundamental_researcher` is preferred for *fetching* raw financial statements.
