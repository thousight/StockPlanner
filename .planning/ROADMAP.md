# Roadmap - StockPlanner API Backend

This roadmap outlines the evolution of the StockPlanner backend into a robust, cloud-synced financial planner API.

## Milestone History
- [v1: API Server & Cloud Sync](.planning/milestones/v1-ROADMAP.md) — Established async foundation, LangGraph persistence, and financial CRUD. (Completed 2026-03-02)
- [v2: Basic Authentication & User Management](.planning/milestones/v2-ROADMAP.md) — Established JWT security flow and multi-tenant data isolation. (Completed 2026-03-02)
- [v3: Conversation History & Memory](.planning/milestones/v3-ROADMAP.md) — Established Redis memory and permanent history storage. (Completed 2026-03-03)
- [v4: Advanced Agents & Financial Context](.planning/milestones/v4-ROADMAP.md) — Specialized agents for SEC, social, and macro narrative. (Completed 2026-03-05)

## Milestone 5: Python Code Execution Agent (Current)
**Goal:** Secure, sandboxed environment for on-the-fly Python execution for complex math and financial analysis.
- [v5: Python Code Execution Agent](.planning/milestones/v5-ROADMAP.md) — Secure runtime (Micro-VM/Wasm) and code generation agent.

### Phase 21: Secure Runtime Implementation
**Goal:** Build the isolated execution engine using WebAssembly (Pyodide) or Micro-VM (E2B).
**Status:** In Progress

### Phase 22: Code Generation & Verification
**Goal:** Create a specialized agent for writing and auditing Python scripts.
**Status:** Planned

### Phase 23: Execution Tooling & Feedback
**Goal:** Link the generator to the sandbox and handle errors.
**Status:** Planned

### Phase 24: Monitoring & Auditing
**Goal:** Finalize security and observability.
**Status:** Planned

## Milestone 6: User Long-term Memory
**Goal:** Persistent user profile and memory using pgvector for personalized advice.
- [v6: User Long-term Memory](.planning/milestones/v6-ROADMAP.md) — pgvector store, extraction agent, and on-demand retrieval.

## Milestone 7: Evaluation & Observability
**Goal:** Self-improving agent prompts via automated evaluations and deep tracing.
- [v7: Evaluation & Observability](.planning/milestones/v7-ROADMAP.md) — Custom traces/spans, LLM-as-a-judge, and automated prompt refinement.

## Milestone 8: Daily Proactive Analysis
**Goal:** Move from reactive chat to proactive financial coaching.
- [v8: Daily Proactive Analysis](.planning/milestones/v8-ROADMAP.md) — Deep research and automated portfolio briefings.

## Milestone 9: OAuth & Google Sign-In
**Goal:** Expand authentication options for better mobile onboarding.
- [v9: OAuth & Google Sign-In](.planning/milestones/v9-ROADMAP.md) — Google Identity integration and account linking.
