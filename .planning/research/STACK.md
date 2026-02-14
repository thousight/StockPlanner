# Technology Stack

**Project:** Personal Financial Assistant
**Researched:** 2024

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **LangChain / LangGraph** | Current | Orchestration | Best-in-class for stateful multi-agent workflows (Supervisor pattern). |
| **Python** | 3.10+ | Runtime | Native ecosystem for AI and Financial libraries (`pandas`, `yfinance`). |
| **Pydantic** | v2 | Data Validation | Strict output parsing is critical for financial data reliability. |

### Data Sources (APIs)
| Technology | Tier | Purpose | Why |
|------------|------|---------|-----|
| **Finnhub.io** | Free | Real-time Stock Data | 60 calls/min limit is generous; covers US stocks, news, and basic fundamentals. |
| **yfinance** | Open Source | Historical Data | Backup for Finnhub; allows deeper historical analysis without API limits (though less stable). |
| **DuckDuckGo Search** | Free | General Research | Best free web search tool for LangChain to answer general "who is CEO" type questions. |

### Infrastructure & Database
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **PostgreSQL** | 14+ | User/Portfolio DB | Structured, reliable storage for user profiles and portfolio snapshots. |
| **SQLite** | (Local) | Dev/Cache | Sufficient for local prototype caching to save API calls. |

### User Interface
| Technology | Purpose | Why |
|------------|---------|-----|
| **Streamlit** | Frontend | Rapid prototyping of data-heavy chat interfaces. Great charts support. |
| **Chainlit** | Chat UI | Alternative if focus is purely conversational (better chat history UX). |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Market Data | **Finnhub** | Alpha Vantage | Alpha Vantage free tier is too restrictive (25 requests/day). |
| Market Data | **Finnhub** | Polygon.io | Polygon is excellent but expensive for hobbyists/startups ($29/mo+). |
| Orchestration | **LangGraph** | AutoGen | LangGraph offers more explicit control over state and routing, which is safer for finance. |

## Installation

```bash
# Core
pip install langchain langchain-openai langgraph

# Financial Data
pip install finnhub-python yfinance

# Utilities
pip install pandas pydantic python-dotenv

# UI
pip install streamlit
```

## Sources

- [Finnhub Pricing/Limits](https://finnhub.io/pricing)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
