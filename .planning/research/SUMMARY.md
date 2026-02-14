# Research Summary: Personal Financial Assistant

**Domain:** Fintech / Personal Finance AI
**Researched:** 2024
**Overall confidence:** HIGH

## Executive Summary

The proposed Personal Financial Assistant aims to bridge the gap for beginners (elderly and young adults) who find standard financial tools intimidating. The research points to a **multi-agent Supervisor architecture** using **LangGraph** as the optimal technical foundation. This allows for specialized "expert" agents (Market Data, News, Planner) to operate independently while a central supervisor manages the workflow.

Data sourcing strategies heavily favor **Finnhub** (generous free tier) for real-time data, backed by **yfinance** for historical depth, ensuring a cost-effective "beginner" product. The User Experience (UX) research highlights a critical need for **"Explain Like I'm 5" (ELI5)** communication styles and high-accessibility design (large text, voice input) to reduce fear and confusion.

Compliance is a major constraint; the system must strictly operate as an **informational tool**, not an advisory one, with robust disclaimers and a refusal to execute trades directly.

## Key Findings

**Stack:** LangGraph (Orchestration), Finnhub (Real-time Data), Streamlit/Chainlit (UI).
**Architecture:** Supervisor Pattern (Router -> Specialized Agents -> Explanation Layer).
**Critical pitfall:** AI Hallucination of financial figures (requires strict tool-based retrieval, not LLM generation).

## Implications for Roadmap

Based on research, suggested phase structure:

1.  **Phase 1: Core Data & Supervisor** - Build the Supervisor node and the Market Data Agent (Finnhub).
    - Addresses: Basic stock checks (Table Stakes).
    - Avoids: Hallucinating prices.

2.  **Phase 2: News & Explanation Engine** - Add the News Agent and the "ELI5" post-processing layer.
    - Addresses: "What is happening?" questions.
    - Focus: UX for beginners (simplification).

3.  **Phase 3: Financial Planning & Profile** - Add the Planner Agent with risk/age-based logic.
    - Addresses: "Am I on track?" questions.
    - Risk: ensuring generic advice vs. specific investment advice (Compliance).

**Phase ordering rationale:**
- Establish truth (Data) first.
- Then make it understandable (News/Explanation).
- Only then interpret it (Planning) to minimize risk of bad advice early on.

**Research flags for phases:**
- Phase 3: Needs deeper research on *legal* specificities of "financial planning" wording in target jurisdictions.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | LangGraph is standard; Finnhub is best-in-class free tier. |
| Features | HIGH | Clear beginner needs (Education > Execution). |
| Architecture | HIGH | Supervisor pattern is well-documented for this complexity. |
| Pitfalls | MEDIUM | Compliance boundaries for AI are evolving rapidly. |

## Gaps to Address

- **User Testing:** Need to validate "Risk Weather Forecast" metaphors with actual elderly/young users.
- **Geographic Scope:** Research assumed US markets (SEC rules); international requires different data/compliance.
