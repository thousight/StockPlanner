# Requirements - Milestone 4: Advanced Agents & Financial Context

This milestone focuses on deepening the analytical capabilities of the agentic team with specialized agents for EDGAR (SEC filings), social media analysis, macro-economic tracking, and market narrative shifts.

## 1. SEC & EDGAR Analysis

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-100** | **SEC Agent**: Dedicated agent for parsing SEC filings (10-K, 10-Q) and extracting structured data. | P0 | [x] |
| **REQ-101** | **Filing Delta**: Capability to compare changes between recent SEC filings to identify new risks. | P1 | [x] |

## 2. Social & Sentiment

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-110** | **Sentiment Researcher**: Agent dedicated to analyzing market mood from news and social media. | P0 | [x] |
| **REQ-111** | **X (Twitter) Integration**: Tooling to fetch recent cashtag tweets and specific user tweets (e.g., political figures). | P1 | [x] |

## 3. Modular Graph Architecture

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-120** | **Parallel Routing**: Supervisor can route to multiple specialized researchers concurrently. | P0 | [x] |
| **REQ-121** | **Analyst Synthesis**: Dedicated Analyst agent to synthesize parallel research results into a cohesive report. | P0 | [x] |

## 4. Macro Economics & Market Narrative

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-130** | **Macro Indicators**: Tooling to fetch key US macroeconomic indicators (GDP, CPI, Payrolls, Interest Rates, DXY) from free sources like FRED. | P0 | [x] |
| **REQ-131** | **Market Narrative Agent**: Specialized agent to synthesize broad market growth narratives and identify shifts using a 7-day lookback cache. | P0 | [x] |
| **REQ-132** | **Research Cache**: Unified caching layer for API responses (News, SEC, Macro, Narrative) to improve performance and reduce API costs. | P0 | [x] |
