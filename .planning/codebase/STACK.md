# Technology Stack

**Analysis Date:** 2025-05-22

## Languages

**Primary:**
- Python 3.x - Used for the entire backend application, including agent logic, data processing, and the Streamlit UI.

**Secondary:**
- None detected.

## Runtime

**Environment:**
- Python 3.x

**Package Manager:**
- pip
- Lockfile: `requirements.txt` present.

## Frameworks

**Core:**
- **LangGraph** (v.latest) - Used for building the multi-agent orchestration graph (`src/graph.py`).
- **LangChain** (v.latest) - Used for LLM abstractions, message structures, and tool integrations (`src/utils/news.py`, `src/agents/research/agent.py`).
- **Streamlit** (v.latest) - Used for the web-based user interface and session management (`src/app.py`).

**Testing:**
- **Pytest** - Used for unit and integration testing (`pytest.ini`, `tests/` directory).

**Build/Dev:**
- **python-dotenv** - Manages environment variables from `.env` files (`src/app.py`).

## Key Dependencies

**Critical:**
- **langchain-openai** - Integration with OpenAI's models (GPT-4o).
- **yfinance** - SDK for fetching market data and stock news from Yahoo Finance.
- **ddgs (duckduckgo-search)** - SDK for performing web searches via DuckDuckGo.
- **sqlalchemy** - SQL Toolkit and ORM for managing the local SQLite database.
- **pydantic** - Data validation and settings management using Python type annotations.

**Infrastructure:**
- **pandas** - Data manipulation and analysis, used for portfolio dataframes (`src/app.py`).
- **plotly** - (Present in `requirements.txt`) Intended for interactive data visualization.
- **beautifulsoup4** & **readability-lxml** - Used for extracting and cleaning content from news articles (`src/utils/news.py`).

## Configuration

**Environment:**
- Configured via `.env` file.
- Key configs required: `OPENAI_API_KEY`.

**Build:**
- `requirements.txt` for dependency management.
- `pytest.ini` for test runner configuration.

## Platform Requirements

**Development:**
- Local Python environment (3.10+ recommended).
- Internet access for OpenAI API, Yahoo Finance, and DuckDuckGo.

**Production:**
- Streamlit Cloud, Heroku, or any Linux/Windows environment supporting Python and persistent local file storage (for `stocks.db`).

---

*Stack analysis: 2025-05-22*
