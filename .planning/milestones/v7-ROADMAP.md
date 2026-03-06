# Roadmap - Milestone 7: Evaluation & Observability

This roadmap focuses on building a self-improving feedback loop for the agent team using in-house tracing and automated evaluations.

## Phase 29: Traces & Spans Schema
**Goal:** Implement the high-performance logging layer for graph execution.
- [ ] Database migration to add `traces` and `spans` tables.
- [ ] Implementation of a `BaseCallbackHandler` to capture LangGraph node-level metrics.
- [ ] Integration of Correlation IDs across the API and agent layers.

## Phase 30: In-house Judge & Automated Evaluation
**Goal:** Implementation of the automated critic agent (LLM-as-a-judge).
- [ ] Build the `CriticAgent` with standardized metrics (Faithfulness, Relevance).
- [ ] Automate the scoring of completed traces and storing results in `eval_results`.
- [ ] Implementation of the `Gold Dataset Generator` to archive high-signal user sessions.

## Phase 31: Failure Mode Analysis & Reporting
**Goal:** Identify which nodes are underperforming.
- [ ] Implementation of the `view_node_performance` database view.
- [ ] Integration of evaluation scores into the `AnalystAgent` feedback loop.
- [ ] A dashboard view (internal/CLI) to see top failing test cases.

## Phase 32: Automated Prompt Refinement Loop
**Goal:** Close the feedback loop by suggesting prompt improvements.
- [ ] Implementation of the `RefinementAgent` to analyze low-score traces.
- [ ] Use "Few-shot" examples from failing traces to generate improved system instructions.
- [ ] Implementation of a "Prompt Registry" to version and track prompt performance over time.
