# Project: StockPlanner

## Core Mission
Building an autonomous, multi-agent financial planning and analysis system. It transforms raw market data (Financials, SEC filings, News, Social sentiment) into deeply personalized investment profiles, identifying institutional moves ("Whale tracking") and distinguishing real narratives from artificial "Hype" (Narrative Intelligence).

## Key Themes
- **Multi-Agent Autonomy:** Moving from single-node logic to a LangGraph **Supervisor/Worker** model for scalable, parallel stock research.
- **Deep Stock Profiling:** Automated gathering of business models, financial health, and growth metrics to ground all investment advice.
- **Whale Tracking:** Scraping and parsing raw SEC 13F filings from EDGAR to track institutional movements as primary analysis context.
- **Narrative Intelligence:** A hybrid approach using both News Sentiment and Social Media (X/Reddit) to detect "bubbles" and artificial market manipulation.
- **Formal Personalization:** Matching stock profiles to a user's explicitly defined risk tolerance, age, and long-term goals.

## Architecture Vision
- **Orchestration:** LangGraph `StateGraph` with a central `Supervisor` node.
- **Frontend:** Streamlit for portfolio management and interactive analysis reports.
- **Backend:** Python + SQLAlchemy (SQLite) for state and portfolio persistence.
- **Agents:** Specialized workers (Financials, Sentiment, WhaleTracker, HypeDetector).

---
*Created: 2026-02-21*
