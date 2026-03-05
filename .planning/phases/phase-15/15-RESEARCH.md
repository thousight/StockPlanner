# Phase 15: SEC & EDGAR Agent - Research

**Date:** 2026-03-04
**Focus:** Ecosystem research for SEC/EDGAR parsing, delta detection, and agentic integration.

## Executive Summary
In 2026, the standard for SEC filing analysis has shifted from fragile regex-based HTML scraping to **Section-Aware Extraction** and **Semantic Delta Detection**. The recommended approach combines official SEC JSON APIs for quantitative data with specialized extraction services (like `sec-api.io`) or XML-aware parsers (`sec-parsers`) for qualitative narrative sections.

## 1. Technical Stack & APIs

### Quantitative Data (Financial Metrics)
- **Tool:** `sec-edgar-api` (Python wrapper for official SEC JSON API).
- **Benefit:** Direct access to "Company Facts" (Net Income, Assets, etc.) without parsing HTML.
- **Usage:** Use this to reconcile or supplement `yfinance` data.

### Qualitative Section Extraction (Risk Factors, MD&A)
- **Top Choice (Paid/Robust):** `sec-api.io` (Extractor API). Handles iXBRL complexities and returns clean text for specific Items (e.g., 1A, 7).
- **Top Choice (Open Source):** `sec-parsers`. Converts filings into XML trees based on structural metadata. Much more reliable than regex.
- **Bulk Downloads:** `sec-edgar-downloader` for local archiving of 10-K, 10-Q, and 8-K filings.

### Essential Filing Items
- **Item 1A:** Risk Factors (Primary focus for delta detection).
- **Item 7:** Management's Discussion and Analysis (MD&A) (Focus for outlook and strategy).
- **Item 1C:** Cybersecurity Disclosures (New mandatory section as of 2024/2025).
- **Item 3:** Legal Proceedings.

## 2. Delta Detection Strategy

Comparing this year's 10-K to last year's is a "Must-Have" for identifying strategy shifts.

### Literal Comparison (Literal Diffs)
- **Tool:** Python's `difflib`.
- **Function:** Identify exact word-for-word additions and removals.
- **Output:** Good for technical logs, but often too noisy for a financial report.

### Semantic Comparison (AI-Driven)
- **Tool:** Gemini 1.5/2.0 Pro or Claude 3.5 Sonnet.
- **Approach:**
    1. Extract Item 1A from 2025 and 2026 filings.
    2. Pass both sections to the LLM with a specific comparison prompt.
    3. LLM identifies "New Risks," "Removed Risks," and "Changed Emphasis."
- **Benefit:** Filters out boilerplate changes (e.g., date updates) and highlights material shifts.

### Vector Similarity (Drift Detection)
- **Tool:** `sentence-transformers` or OpenAI/Gemini Embeddings.
- **Usage:** Compare the embedding of the entire section. A cosine similarity score below **0.90** flags a "Material Change" that warrants a deep-dive.

## 3. Implementation Details for StockPlanner

### Integration Pattern
- **Standalone Tool:** Create an `SECSourceTool` that the `ResearchAgent` can invoke.
- **Workflow:**
    1. `ResearchAgent` identifies the ticker and needs deep risk analysis.
    2. `SECSourceTool` fetches the latest 10-K/Q URLs for the ticker.
    3. Tool extracts relevant sections and performs a YoY delta if a previous filing exists.
    4. Findings are summarized by an LLM and returned to the agent.

### Caching & Rate Limiting
- **Caching:** Store parsed sections and summaries in a new `SECCache` table (or extend `NewsCache`). Cache for **7 days** as 10-K/Qs are static.
- **Compliance:** Every request to SEC.gov **MUST** include a descriptive `User-Agent` header (e.g., `StockPlanner (admin@example.com)`). Failure to do so leads to IP blocking.

## 4. Validation Architecture

To ensure the SEC parsing and delta detection logic works correctly without hitting SEC rate limits or incurring high LLM costs during CI/CD, the following architecture is recommended:

### Unit Testing with Mocked HTML/JSON
- **Fixture-Based Parsing:** Use a `tests/fixtures/sec/` directory containing static HTML/iXBRL files of known filings (e.g., AAPL 10-K 2025).
- **Decoupled Logic:** The parser should accept raw strings or local file paths, allowing tests to run in milliseconds without network calls.
- **Boundary Tests:** Specifically test the "Section Extractor" against malformed filings or those with unusual headers to verify the fallback logic.

### Integration Testing (SEC Mocking)
- **Tool:** `pytest-mock` or `responses`.
- **Strategy:** Mock the `requests.get` or `aiohttp` calls to the SEC EDGAR URLs. This verifies that the tool correctly constructs URLs and handles 403 (Rate Limit) or 404 (Filing not found) errors gracefully.

### Semantic Delta Verification (Golden Files)
- **Strategy:** Maintain a "Golden Pair" of filing sections (e.g., 2024 vs 2025 Risk Factors for a specific company) and a corresponding "Golden Summary" of the expected delta.
- **Verification:** Run the delta detection tool against this pair and use an LLM-based evaluator (or simple keyword matching) to verify that the generated summary identifies the key material changes known to exist in that pair.

### E2E Report Verification
- **Strategy:** Run a full graph interaction for a specific ticker (e.g., "Analyze MSFT") using mocked SEC and Market Data.
- **Verification:** Confirm that the final `Report` object contains a section interleaved with "SEC Insights" and that the data correctly reflects the content of the mocked filings.

## 5. Potential Pitfalls

- **Filing Inconsistency:** Older filings or small-cap companies may use older HTML formats that break standard parsers.
- **Token Limits:** 10-K sections can exceed 30k tokens. Use large-context models (Gemini/Claude) or a "Section-by-Section" summarization approach.
- **8-K Noise:** 8-Ks are high-frequency. Filter by "Materiality" or only look at the last 30 days to avoid overwhelming the report.

## 6. Recommended Next Steps

1. **Verify SEC-API Key:** Determine if we use the paid `sec-api.io` for robustness or stick to `sec-parsers` + official SEC API for a free tier.
2. **Infrastructure:** Create `src/graph/tools/sec.py` to house the new extraction logic.
3. **Database:** Add a migration for `sec_filing_cache` to store extracted text and summaries.

---

*Phase: 15-sec-edgar-agent*
*Research completed: 2026-03-04*
