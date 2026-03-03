# Context - Phase 8: Test Coverage Expansion

This document captures implementation decisions for Phase 8 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Module Prioritization & Targets
- **Core Priority:** Equal focus on **Agent Reasoning Nodes** and the **Service Layer** (Math/FX logic).
- **100% Path Coverage:** The **Financial Math** (Multi-currency Average Cost Basis) in `src/services/portfolio.py` must achieve 100% path coverage.
- **Infrastructure:** Include tests for the **FastAPI Lifespan** and background task scheduler startup in `main.py`.
- **Utilities:** Prioritize unit tests for shared functions in the `utils/` directory (prompt formatting, news parsing).

## 2. Internal Agent Verification
- **Research Agent:** Verification must include specific **Tool Planning** checks (verifying the correct tools and arguments are selected).
- **Supervisor Agent:** Test routing decisions for **Happy Path** inputs to ensure correct agent handoff.
- **Analyst Agent:** Implement **Node-level Verification** for the internal debate subgraph (verifying Bull and Bear nodes individually).
- **Auto-Titling:** Implement **Comprehensive Verification** to ensure appropriate titles are generated for a wide range of topics.

## 3. Lifecycle & Task Simulation
- **Cleanup Logic:** Use **Mock Result Mocking** for SQL delete operations rather than seeding physical records.
- **Task Execution:** Trigger background maintenance functions via **Direct Function Calls** in tests rather than through the APScheduler clock.
- **Resilience:** Explicitly **Verify Fault Tolerance** by simulating failures in background tasks to ensure they do not crash the API server.

## 4. Edge Case & Stress Testing
- **Data Gaps:** Test how tools and services handle **Empty External Data** (e.g., yfinance returning no history).
- **Timeouts:** Verify the graph's **Auto-Retry logic** by simulating LLM/API timeouts.
- **Input Stress:** Perform **Input Resilience** tests using malformed, nonsensical, or extremely long user messages.
- **Concurrency:** Implement integration tests to **Verify 409 Conflicts**, simulating multiple simultaneous requests to the same `thread_id`.
