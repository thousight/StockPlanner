# Phase 1 Context: Multi-Agent Core Refactor

## 1. Agent Autonomy & Definition
- **Persona-Driven:** Each worker agent has a dedicated `prompts.py` and `node.py` in its own directory, defining a specific "persona" to guide its reasoning.
- **Supervisor Decomposition:** The Supervisor agent performs high-level planning, decomposing the user prompt into steps, agent assignments, and dependencies while enforcing global constraints before delegating.
- **Local Planning (Research):** The Research agent must generate a specific `ResearchPlan` (queries, sources, expected data) based on its delegated task before executing tools.
- **Context-Aware Analysis (Analyst):** The Analyst agent evaluates all given context. If gaps are identified, it explicitly requests more information from the Research agent; otherwise, it performs the final analysis.
- **Simplified News Utility:** The News agent is refactored into a focused URL-parsing and content-summarization workflow for the Research agent to utilize.
- **Direct Communication:** Workers can communicate directly (e.g., Analyst -> Research for more data) while maintaining their own internal "stop" logic.

## 2. Worker Findings & Data Handling
- **Format:** Workers return findings in Natural Language, optimized for direct inclusion in the final report.
- **Conflict Resolution:** Data conflicts (e.g., differing price targets) must be resolved by the worker agent before reporting.
- **Citations:** Simplified citation style—URLs only.
- **Metadata:** Every finding must include a "Confidence Score" (0-100) to assist in weighing the evidence.

## 3. User Experience (Streamlit)
- **Thinking Process:** Only high-level "thinking" steps (planning/actions) are displayed; raw logs and self-correction are hidden.
- **Adversarial Debate:** The internal debate details (Positive vs. Negative arguments) are surfaced to the user as expandable rows, allowing for deep-dives into the "fight" behind the final synthesis.
- **Layout:** Expandable rows (`st.status`) for each worker to manage parallel execution visualization.
- **Success Indicators:** A simple checkmark indicates completion.
- **Persistence:** Research history is preserved for the duration of the session.

## 4. Deferred Ideas (Future Phases)
- **Phase 5 (Generic Personal Assistant):** Refactor the domain-specific constraints to allow the Researcher and Analyst agents to handle broader life queries (e.g., travel, health, productivity) based on the user's profile, transforming the app from a stock planner into a holistic decision-support system.
