# Project: StockPlanner

## Vision

A comprehensive financial planner application that collects user financial information and uses a multi-agent LangGraph orchestration to provide personalized financial suggestions. This repository serves as the RESTful API backend for a Flutter-based mobile UI.

## Tech Stack

- **Orchestration**: LangGraph
- **LLM Integration**: LangChain, OpenAI (GPT-4o)
- **API Framework**: FastAPI (Targeted for Milestone 1)
- **Data Layer**: Railway (PostgreSQL)
- **Market Data**: yfinance, DuckDuckGo Search
- **Memory**: PostgreSQL (Long-term), Redis (Short-term, targeted for Milestone 3)
- **Verification**: Pytest

## Current State
- **Shipped:** v3.0 (2026-03-03) — Conversation History & Memory.
- **Verification:** 132 tests ensure system stability, protocol compliance, financial logic, and cross-user security.

<details>
<summary>Previous Shipped Milestones</summary>
- **Shipped:** v1.0 (2026-03-02) — API Server & Cloud Sync.
- **Shipped:** v2.0 (2026-03-02) — Basic Authentication & User Management.
- **Security:** Argon2id hashing, JWT Access/Refresh tokens with rotation, and strict multi-tenant isolation ("Stealth 404") are fully operational.
</details>

## Next Milestone Goals (Milestone 4: Advanced Agents & Financial Context)
- **Specialized Agents:** Create dedicated agents for EDGAR (SEC filings) and social media analysis.
- **Modularity:** Refactor the supervisor graph for improved routing and stability.
- **Deep Research:** Implement narrative and sentiment analysis for financial news.

## Core Principles

- **API-First**: Headless RESTful backend designed for high-performance mobile clients.
- **Cloud-Synced**: Uses Railway for cross-device data persistence.
- **State-Driven**: Entire workflow and conversation history are managed by structured LangGraph states.

## Key Decisions

- **[2026-02-28] Multi-Agent Architecture**: Moved from single-agent to a supervisor-led multi-agent mesh for better specialization.
- **[2026-02-28] Financial Planner Pivot**: Expanded scope from stock analysis to general financial planning with a Flutter mobile frontend and Railway cloud integration.

## Constraints

- Dependent on OpenAI API for core reasoning.
- Market data via yfinance (limited to what Yahoo provides).
- Railway connection and authentication requirements for mobile clients.
