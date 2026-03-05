# Phase 17 Research: Modular Graph

## 1. Parallel Research Architecture
- **Pattern:** **Dynamic Fan-out (Map-Reduce)** using the LangGraph `Send` API.
- **Workflow:** `Supervisor` -> `Parallel Researchers (Send)` -> `Analyst (Join)`.
- **Fan-out:** The `Supervisor` will return a list of `Send` objects, one for each specialized researcher it wants to activate.
- **Fan-in:** The `Analyst` node will be the common destination for all researcher nodes. LangGraph automatically synchronizes and waits for all parallel branches to complete before executing the `Analyst`.
- **Concurrency:** Uses `config={"max_concurrency": N}` to control the number of simultaneous LLM calls.

## 2. Specialized Researcher Prompts
### FundamentalResearcher
- **Focus:** Institutional-grade SEC analysis (10-K, 10-Q, 8-K).
- **Thinking Process:** Contextualize -> Quantitative Extraction -> Qualitative "Diff" -> Fundamental Sentiment.
- **Output:** Structured report on intrinsic value, operational health, and hidden risks.

### SentimentResearcher
- **Focus:** High-velocity market mood from News, X, and Reddit.
- **Thinking Process:** Distinguish signal from noise -> Normalizing Sentiment (-1.0 to 1.0) -> Source Credibility Weighting.
- **Output:** Multi-dimensional sentiment profile with velocity indicators.

### MacroResearcher
- **Focus:** Global economic indicators, Fed policy, and sector-wide trends.
- **Thinking Process:** Geopolitical impact -> Interest rate environment -> Commodity price spikes.
- **Output:** Broader economic context for the investment thesis.

## 3. State Management & Communication
- **Reducers:** The current `agent_interactions` key uses `Annotated[List, operator.add]`, which is essential for parallel execution. It allows each researcher to append its findings without overwriting others.
- **Analyst Context:** The `Analyst` will read the accumulated `agent_interactions` list to build a comprehensive view of the specialized data gathered by the research squad.
- **Follow-up Routing:** The `Analyst` will be empowered to route back to specialized researchers with specific, atomic questions using the same `Send` pattern.

## 4. UI Observability
- **Node Branding:** Each specialized researcher will have a unique node ID (e.g., `fundamental_researcher`, `sentiment_researcher`) which will be streamed to the UI, providing the user with transparency into the "expert squad" workflow.
