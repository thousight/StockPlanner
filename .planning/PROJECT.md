# Project: StockPlanner

## Vision

A comprehensive financial planner application that collects user financial information and uses a multi-agent LangGraph orchestration to provide personalized financial suggestions and adversarial stock analysis. This repository serves as the RESTful API backend for a Flutter-based mobile UI.

## Tech Stack

- **Orchestration**: LangGraph
- **LLM Integration**: LangChain, OpenAI (GPT-4o)
- **API Framework**: FastAPI (Targeted for Milestone 1)
- **Data Layer**: Supabase (PostgreSQL)
- **Market Data**: yfinance, DuckDuckGo Search
- **Memory**: PostgreSQL (Long-term), Redis (Short-term, targeted for Milestone 3)
- **Verification**: Pytest

## Core Principles

- **API-First**: Headless RESTful backend designed for high-performance mobile clients.
- **Cloud-Synced**: Uses Supabase for cross-device data persistence.
- **Adversarial Analysis**: Uses a 'Bull vs. Bear' debate pattern to provide unbiased financial insights.
- **State-Driven**: Entire workflow and conversation history are managed by structured LangGraph states.

## Key Decisions

- **[2025-03-05] Multi-Agent Architecture**: Moved from single-agent to a supervisor-led multi-agent mesh for better specialization.
- **[2026-02-28] Streamlit UI Removal**: Pivoted to a headless architecture to prioritize the robustness of the agentic engine.
- **[2026-02-28] Explicit Debate Metadata**: Restored `debate_output` in `AgentInteraction` to ensure confidence scores and adversarial arguments are captured.
- **[2026-02-28] Financial Planner Pivot**: Expanded scope from stock analysis to general financial planning with a Flutter mobile frontend and Supabase cloud integration.

## Constraints

- Dependent on OpenAI API for core reasoning.
- Market data via yfinance (limited to what Yahoo provides).
- Supabase connection and authentication requirements for mobile clients.
