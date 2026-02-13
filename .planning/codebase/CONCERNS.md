# Codebase Concerns

**Analysis Date:** 2025-02-13

## Tech Debt

**Database Session Management:**
- Issue: In `src/web/app.py`, sessions are obtained via `next(get_db())` but never explicitly closed, relying on the generator's `finally` block which may not trigger reliably in Streamlit's execution model.
- Files: `src/web/app.py`, `src/database/database.py`
- Impact: Potential connection leaks or locked database files over time, especially with SQLite.
- Fix approach: Use a context manager or explicitly close the session at the end of the script or interaction.

**Error Recovery in Agents:**
- Issue: The graph is strictly linear (`research` -> `analyst` -> `cache_maintenance`). If research data is missing or corrupted, the analyst node still proceeds with incomplete data.
- Files: `src/agents/graph.py`, `src/agents/nodes/research/node.py`
- Impact: AI analyst may provide recommendations based on "0" prices or empty news, leading to low-quality or misleading advice.
- Fix approach: Implement validation in research node and potentially add a retry loop or conditional edges in LangGraph to handle failures.

**Redundant Database Connections:**
- Issue: `get_summary` and `cache_maintenance_node` manually create and close `SessionLocal()` instances. When `get_macro_economic_news` runs with `ThreadPoolExecutor`, multiple sessions are opened simultaneously.
- Files: `src/agents/nodes/research/utils.py`, `src/agents/nodes/nodes.py`
- Impact: Inefficient resource usage.
- Fix approach: Pass a shared session through the state or use a more robust session pooling mechanism.

## Performance Bottlenecks

**News Summarization Latency:**
- Problem: `get_summary` is called for every news item. While it uses `ThreadPoolExecutor`, the latency of LLM calls for each article summary significantly slows down the research phase.
- Files: `src/agents/nodes/research/utils.py`
- Cause: Multiple sequential or semi-parallel LLM calls for content summarization.
- Improvement path: Optimize parallel execution limits, use faster models for summarization (e.g., GPT-4o-mini), or further improve caching strategies.

**Truncated Content for Analysis:**
- Problem: Articles are truncated to 4000 characters and summaries to 500 characters.
- Files: `src/agents/nodes/research/utils.py`, `src/agents/nodes/analyst/node.py`
- Cause: Fear of exceeding LLM context limits.
- Improvement path: Implement dynamic context management or use a model with a larger context window while being selective about which content is included.

## Fragile Areas

**Third-Party Scrapers:**
- Files: `src/agents/nodes/research/utils.py`
- Why fragile: Relies on `yfinance` and `duckduckgo_search` (via `ddgs`), both of which are unofficial and prone to breaking when target site structures change.
- Safe modification: Encapsulate these tools behind clear interfaces to allow easy replacement with official APIs (e.g., Alpha Vantage, NewsAPI) if needed.
- Test coverage: Existing tests mock these, but integration tests with real data are missing.

**Article Content Extraction:**
- Files: `src/agents/nodes/research/utils.py` (`fetch_article_content`)
- Why fragile: Uses `readability` and `BeautifulSoup` to scrape arbitrary URLs. Many news sites have paywalls, anti-bot protections (Cloudflare), or complex JS-rendered content that simple `requests` cannot handle.
- Safe modification: Consider using a dedicated scraping service or an LLM-based web loader that handles JavaScript.

## Missing Critical Features

**Current Portfolio Valuation:**
- Problem: The UI displays "Total Invested" based on cost basis but lacks a "Current Value" metric.
- Blocks: Users cannot see their actual profit/loss in real-time.
- Files: `src/web/app.py`

**Real-time Logging:**
- Problem: Most errors are handled with `print()` or `st.error()`.
- Blocks: Debugging issues in a deployed environment without access to stdout.
- Files: Throughout `src/`

## Test Coverage Gaps

**Integration Testing:**
- What's not tested: The full LangGraph workflow and the database-to-UI flow.
- Files: `src/agents/graph.py`, `src/web/app.py`
- Risk: Changes in state structure or DB schema could break the app without unit tests failing.
- Priority: Medium

---

*Concerns audit: 2025-02-13*
