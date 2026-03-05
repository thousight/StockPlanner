# Phase 17 Context: Modular Graph

## Overview
This phase refactors the graph topology to introduce specialized researcher nodes. The primary goal is to move from a single "Research" node to a parallel research layer where expert agents (Fundamental, Sentiment, Macro) gather high-signal data independently and report back to the Analyst Brain.

## Implementation Decisions

### 1. Specialized Researcher Squad
- **FundamentalResearcher:** Owns "hard" data tools (`get_stock_financials`, `get_sec_filing_section`, `get_sec_filing_delta`).
- **SentimentResearcher:** Owns "pulse" data tools (`get_stock_news`, `get_market_sentiment`, X API).
- **MacroResearcher:** Preparatory node for Phase 18. Will handle broad economic queries.
- **Shared Tools:** Both Fundamental and Sentiment researchers have access to generic `web_search`.

### 2. Graph Topology & Parallelism
- **Parallel Fan-Out:** The `Supervisor` can trigger multiple research nodes (Fundamental, Sentiment, Macro) simultaneously based on the user's query.
- **Fan-In Synthesis:** The `Analyst` node acts as the barrier; it must wait for all active research nodes to finish before starting the Bull/Bear debate.
- **Debate Sub-Graph:** The Bull/Bear debate remains a specialized sub-graph encapsulated within the `Analyst` node to maintain logic isolation.

### 3. Orchestration & Routing
- **Supervisor Role:** Acts as a dispatcher. It analyzes the user request and identifies which specialized researchers to activate. It does *not* dictate specific tool calls; each researcher analyzes the problem locally to decide its own plan.
- **Specific Follow-ups:** The `Analyst` is empowered to route back to specialized researchers with **specific, targeted questions** (e.g., "Is there a recent supply chain disruption in Taiwan?") rather than generic "need more data" requests.
- **State Management:** Continue using the `agent_interactions` list for communication. Agents read the history to build their local context.

### 4. Observability & Branding
- **Node Visibility:** The UI will explicitly display specialized node names (e.g., `node:fundamental_research`, `node:sentiment_research`) to give the user transparency into the expert squad's work.

## Code Context
- **Graph:** Significant refactor of `src/graph/graph.py` to support parallel branches and new nodes.
- **Agents:** Split `src/graph/agents/research/agent.py` into three specialized files or classes.
- **Prompts:** Update `Supervisor` to understand the specialized researcher roles. Update `Analyst` to handle specific follow-up routing logic.

## Deferred Ideas (Out of Scope)
- Structured `research_data` dictionary in state (sticking to `agent_interactions` for now).
- Technical/Chart Analyst node (staying with the three research experts).
