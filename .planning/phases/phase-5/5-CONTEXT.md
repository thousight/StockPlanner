# Context - Phase 5: Agentic Flow Refinement

This document captures implementation decisions for Phase 5 of the StockPlanner API Backend to guide downstream research and planning.

## 1. Generalized Report Definition & Schema
- **Report Scope:** Reports are no longer tied strictly to stock tickers. They represent high-level synthesis for any topic (e.g., Stock trends, Real Estate analysis, Macroeconomic research).
- **Unified Subjectivity:** The `symbol` field in the `Reports` table will be replaced or augmented by a **Unified Topic Field** (e.g., "NVDA", "Seattle Housing", "Gold Market").
- **Categorization:** Every report must have an explicit **Category** (e.g., STOCK, REAL_ESTATE, MACRO, FUND, GENERAL).
- **Presentation:** Reports will include an explicit **Title** field for faster UI rendering.
- **Off-Topic Exclusion:** Results from the "Off-Topic" agent will remain in the chat history only and will **not** generate entries in the `Reports` table.

## 2. Conditional Interrupt & Safety Policy
- **Strict Approval Policy:** All report generation (regardless of category) will trigger a safety interrupt for human oversight.
- **Threshold Gating:** To improve UX, the system will apply a **Threshold Check**: very short or simplistic responses that don't meet a complexity threshold (e.g., no data points or adversarial arguments) will bypass the interrupt and commit silent updates.
- **Action Overrides:** Any report containing specific action keywords (e.g., BUY, SELL, TRADE, INVEST) will **force** an interrupt, bypassing the complexity threshold.
- **Interrupt Payload:** The safety interrupt SSE event must include a **Full Preview** of the report's metadata: Title, Topic, and Category.

## 3. Classification & Retrieval
- **Filtering:** The API must support filtering reports by **Category** and searching by **Keywords** (e.g., "Seattle", "NVDA", "Gold").
- **Auto-Tagging:** The agentic engine will automatically generate 2-3 **Tags** per report (e.g., #growth, #risk) for enhanced organization.
- **Thread Linkage:** Every report must maintain a link to its **Source Thread ID**, allowing the mobile client to navigate from a report back to the original conversation.
- **Trend Grouping:** "Market Trends" reports will be organized by **Region** (e.g., US, Global, Asia).

## 4. User Experience & Auto-Commit Flow
- **Rejection Path:** If a user rejects a report commit during the interrupt phase, the agent must **Acknowledge & Continue** the conversation rather than ending the turn.
- **Success Signal:** The system will use **Silent Success** logic; once a commit is approved and completed, the client relies on the final token and status events rather than a new ID-specific event.
- **Silent Updates:** When a report is automatically updated (silent commit), the system must send a specific **Update Notification** SSE event so the client can refresh its background data.
