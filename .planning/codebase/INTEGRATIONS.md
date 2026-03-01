# External Integrations

**Analysis Date:** 2025-05-22

## APIs & External Services

**LLM Provider:**
- **OpenAI** - Primary LLM provider for all agent functions (GPT-4o).
  - SDK/Client: `langchain-openai`
  - Auth: `OPENAI_API_KEY` (env var)

**Market Data:**
- **Yahoo Finance** - Provides historical/current financial data and news.
  - SDK/Client: `yfinance`
  - Auth: None (publicly accessible).

**Web Search:**
- **DuckDuckGo** - Provides general web search capabilities.
  - SDK/Client: `ddgs` (duckduckgo-search)
  - Auth: None (publicly accessible).

## Data Storage

**Databases:**
- **SQLite**
  - Connection: Local file `stocks.db` in project root.
  - Client: `sqlalchemy` ORM.
  - Usage: Portfolio transaction history (`src/database/models.py`) and news summary caching (`src/utils/news.py`).

**File Storage:**
- **Local filesystem only**
  - Storage of `stocks.db`.

**Caching:**
- **Local SQLite Cache**
  - Implementation: `src/utils/news.py` caches summaries of fetched news articles with a 7-day TTL.

## Authentication & Identity

**Auth Provider:**
- **Local Env Key (OpenAI)**
  - Implementation: API keys provided via `.env` file and validated during app startup (`src/app.py`).

## Monitoring & Observability

**Error Tracking:**
- **None** - Local console output and Streamlit error UI only.

**Logs:**
- **Custom Agent Logger**
  - Decorator `@with_logging` in `src/agents/utils.py` catches and prints agent tracebacks to console.

## CI/CD & Deployment

**Hosting:**
- **Streamlit (Implicitly)** - Designed to be run as a Streamlit application.

**CI Pipeline:**
- **None detected** - No explicit GitHub Actions or other CI/CD files.

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY`: Critical for LLM operations.

**Secrets location:**
- `.env` file (local) - Standardized by `python-dotenv`.

## Webhooks & Callbacks

**Incoming:**
- **None**

**Outgoing:**
- **None**

---

*Integration audit: 2025-05-22*
