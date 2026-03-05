# Phase 15: SEC & EDGAR Agent - Context

**Gathered:** 2026-03-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Dedicated tool and logic for parsing SEC filings (10-K, 10-Q, 8-K) and structured reports. The output will be interleaved into relevant report sections to provide deep regulatory and narrative context.

</domain>

<decisions>
## Implementation Decisions

### Filing Coverage & Depth
- **Primary Filings:** Focus on 10-K (Annual), 10-Q (Quarterly), and 8-K (Current).
- **Extraction:** AI-generated summaries of key sections: Risk Factors, MD&A, and Financials.
- **8-K Handling:** Treat 8-Ks as news events and merge them into the general research flow.
- **Insider Trading:** Report only "Significant" trades (e.g., >$1M or CEO/CFO trades) from Form 4.

### Data Extraction vs. Qualitative Analysis
- **Financial Data:** Trust yfinance for primary numbers; use EDGAR purely for narrative, footnotes, and management commentary.
- **Sentiment:** Perform general sentiment analysis of the entire filing.
- **Legal:** Provide a high-level summary of the "Legal Proceedings" section (Item 3 in 10-K).
- **Outlook:** Extract and summarize management's "Outlook" and forward-looking guidance.

### Integration with Existing Agents
- **Workflow Role:** Standalone tool — the "Research" agent calls the SEC tool when it needs deep regulatory data.
- **Output Presentation:** Interleave SEC insights into relevant report sections (e.g., SEC risks in the "Risks" section).
- **Cross-Agent Communication:** Use Context Injection to pass SEC summaries to the "Analyst" agent for valuation/sentiment adjustment.
- **Streaming:** Final Block — Send the complete SEC analysis only once parsing and summarization are finished.

### Temporal Scope & Comparisons
- **Comparison:** YoY Comparison (Current vs. Previous year same period).
- **Delta Detection:** General summary of "What's New" (qualitative summary of wording/strategy changes).
- **Caching:** Cache SEC data for one week.
- **Coverage Depth:** AI Summary only (no quotes or direct snippets).

### Claude's Discretion
- Selection of specific AI models for summarization.
- Exact regex or parsing logic for section identification within raw EDGAR HTML/text.
- Formatting of the interleaved sections within the final report.

</decisions>

<specifics>
## Specific Ideas

- "I want to see if they've changed how they talk about their risks compared to last year."
- "Focus on the narrative 'why' behind the numbers yfinance already gives us."

</specifics>

<deferred>
## Deferred Ideas

- Social media sentiment analysis — Phase 16.
- Refactoring the supervisor graph for specialized routing — Phase 17.
- Multi-year trend analysis (3+ years) — future milestone.

</deferred>

---

*Phase: 15-sec-edgar-agent*
*Context gathered: 2026-03-04*
