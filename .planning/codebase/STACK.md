# Technology Stack

**Analysis Date:** 2025-02-13

## Languages

**Primary:**
- Python 3.x - Core application logic, agents, data processing, and web interface.

## Runtime

**Environment:**
- Python 3.x

**Package Manager:**
- pip
- Lockfile: `requirements.txt` present.

## Frameworks

**Core:**
- **Streamlit** - Used for the web-based user interface (`src/web/app.py`).
- **LangGraph** - Manages the agentic workflow and state transition logic (`src/agents/graph.py`).
- **LangChain** - Provides abstractions for LLM interactions and message handling (`src/agents/nodes/analyst/node.py`, `src/agents/nodes/research/utils.py`).

**Testing:**
- **Pytest** - Test runner and framework (`pytest.ini`, `tests/` directory).

**Data/UI:**
- **Pandas** - Data manipulation and analysis (`src/web/app.py`).
- **Plotly** - Interactive visualizations (imported in `requirements.txt`, used in `src/web/app.py`).

## Key Dependencies

**Critical:**
- `langchain-openai` - OpenAI LLM integration for analysis and summarization.
- `yfinance` - Real-time and historical market data retrieval (`src/agents/nodes/research/utils.py`).
- `sqlalchemy` - ORM for database interactions (`src/database/database.py`).
- `pydantic` - Data validation and settings management (e.g. `AgentState` in `src/agents/state.py`).

**Infrastructure:**
- `python-dotenv` - Environment variable management (`src/web/app.py`).
- `requests` / `beautifulsoup4` / `readability-lxml` - Web scraping and content extraction for news analysis (`src/agents/nodes/research/utils.py`).
- `ddgs` - DuckDuckGo Search for supplemental research (`src/agents/nodes/research/utils.py`).

## Configuration

**Environment:**
- Configured via `.env` file (loaded using `python-dotenv`).
- Key configs required: `OPENAI_API_KEY`.

**Build:**
- None (standard Python project).

## Platform Requirements

**Development:**
- Python 3.8+ recommended.
- Local SQLite database (`stocks.db`).

**Production:**
- Streamlit Cloud or any cloud provider supporting Python and SQLite.

---

*Stack analysis: 2025-02-13*
