# Requirements

## Overview
A personal financial assistant designed for beginners (elderly, young adults) to improve financial health through education and simplified analysis. The system uses a multi-agent architecture to provide data, news, and planning advice in an accessible "Explain Like I'm 5" format.

## User Requirements
- **Beginner-Friendly:** Users must be able to interact via natural language without understanding financial jargon.
- **Trust & Safety:** Users must feel safe; the system must clearly distinguish between facts and general educational guidance (no "hot stock picks").
- **Accessibility:** Text should be large, clear, and easy to read. Complex concepts should be explained with metaphors.
- **Portfolio Tracking:** Users should be able to input their holdings to get relevant news and performance updates.

## Functional Requirements
1.  **Core Agent System (LangGraph):**
    - **Supervisor Agent:** Routes user queries to the appropriate specialized agent.
    - **Market Data Agent:** Fetches real-time/delayed stock prices and basic fundamentals (Market Cap, P/E) using Finnhub/yfinance.
    - **News Agent:** Fetches and summarizes recent news for specific companies or the general market.
    - **Planner Agent:** Provides general financial planning principles based on user age and risk tolerance.
    - **Explanation Agent:** Rewrites technical outputs into simple, plain English (ELI5).

2.  **Data Management:**
    - **Stock Data:** Integration with Finnhub (primary) and yfinance (history).
    - **User Data:** Local SQLite database to store user portfolio (Symbol, Quantity, Avg Cost) and risk profile.

3.  **User Interface:**
    - **Chat Interface:** Primary mode of interaction.
    - **Dashboard:** Simple view of portfolio value and "Risk Weather" (volatility indicator).

## Non-Functional Requirements
- **Compliance:** System must include hardcoded disclaimers. It must NOT execute trades or offer personalized investment advice (RIA compliance).
- **Latency:** Chat responses should be reasonable (streaming tokens preferred).
- **Cost:** Use free tiers of APIs where possible (Finnhub Free Tier).

## Constraints
- **Local Execution:** MVP runs locally (Streamlit/Python).
- **No Real Money:** No integration with brokerages for trading.
