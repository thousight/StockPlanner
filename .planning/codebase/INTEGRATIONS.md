# External Integrations

**Analysis Date:** 2025-02-13

## APIs & External Services

**LLM & Intelligence:**
- **OpenAI** - Used for financial news summarization and portfolio analysis.
  - SDK/Client: `langchain-openai` (ChatOpenAI)
  - Auth: `OPENAI_API_KEY` (via env var or UI input)

**Market Data:**
- **Yahoo Finance** - Primary source for stock prices, fundamental info, and stock-specific news.
  - SDK/Client: `yfinance`
  - Auth: None required (Public API)

**Search:**
- **DuckDuckGo** - Used for macroeconomic and general financial news search.
  - SDK/Client: `ddgs` (DuckDuckGo Search)
  - Auth: None required

## Data Storage

**Databases:**
- **SQLite** (Local)
  - Connection: `sqlite:///stocks.db`
  - Client: `SQLAlchemy`
  - Purpose: Stores portfolio transactions, holdings, and news summary cache.

**File Storage:**
- **Local filesystem only** - Used for the SQLite database file and cache.

**Caching:**
- **SQL-based Cache** - News article summaries are cached in the `cache` table of the SQLite database to avoid redundant LLM calls (`src/database/models.py`, `src/database/crud.py`).

## Authentication & Identity

**Auth Provider:**
- **None/Custom** - Currently relies on the user providing an `OPENAI_API_KEY` in the UI or environment. No user-level login for the MVP.

## Monitoring & Observability

**Error Tracking:**
- **None** - Errors are currently logged to console/terminal.

**Logs:**
- Standard Python `print` and `traceback` logging.

## CI/CD & Deployment

**Hosting:**
- Not explicitly defined, but designed for Streamlit-compatible hosts (e.g., Streamlit Community Cloud).

**CI Pipeline:**
- None detected.

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY`: Required for AI-powered features.

**Secrets location:**
- `.env` file (local development).

## Webhooks & Callbacks

**Incoming:**
- None.

**Outgoing:**
- None.

---

*Integration audit: 2025-02-13*
