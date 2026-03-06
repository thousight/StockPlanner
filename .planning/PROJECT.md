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
- **Shipped:** v4.0 (2026-03-05) — Advanced Agents & Financial Context.
- **Verification:** 132 tests ensure system stability, protocol compliance, financial logic, and cross-user security.

<details>
<summary>Previous Shipped Milestones</summary>
- **Shipped:** v1.0 (2026-03-02) — API Server & Cloud Sync.
- **Shipped:** v2.0 (2026-03-02) — Basic Authentication & User Management.
- **Shipped:** v3.0 (2026-03-03) — Conversation History & Memory.
- **Security:** Argon2id hashing, JWT Access/Refresh tokens with rotation, and strict multi-tenant isolation ("Stealth 404") are fully operational.
</details>

## Next Milestone Goals (Milestone 5: Python Code Execution Agent)
- **Secure Sandbox:** Build an isolated execution runtime (Micro-VM or Wasm) for code execution.
- **Code Generation:** Specialized agent for writing and auditing Python analysis scripts.
- **Financial Logic:** Enable agents to perform complex portfolio math and currency translations.

## Upcoming Milestones
- **Milestone 6: User Long-term Memory**: Persistent user profile and memory using pgvector for personalized advice.
- **Milestone 7: Evaluation & Observability**: Self-improving agent prompts via automated evaluations and deep tracing.
- **Milestone 8: Daily Proactive Analysis**: Move from reactive chat to proactive financial coaching.
- **Milestone 9: OAuth & Google Sign-In**: Integration with Google Identity Services for better onboarding.

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
