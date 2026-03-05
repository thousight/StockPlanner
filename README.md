# Stock Planner Agent

An AI-powered stock analysis and portfolio management tool. This application uses LangGraph to orchestrate a team of AI agents (Researcher and Analyst) to analyze your stock portfolio, fetch real-time news, and provide actionable investment recommendations.

## Features

- **Portfolio Management**: Track your stock holdings, average cost, and performance.
- **AI Research Agent**:
  - Fetches real-time stock data and company info using `yfinance`.
  - Aggregates macro-economic news from multiple sources.
  - Scrapes and summarizes news articles using AI (`gpt-4o`).
- **AI Analyst Agent**:
  - Analyzes portfolio performance and valuation.
  - Reviews summarized news for sentiment and impact.
  - Generates comprehensive "Buy", "Sell", or "Hold" reports.
- **News Caching**: Optimized with a SQLite database to cache news summaries for 24 hours, reducing API costs and latency.
- **Interactive UI**: Built with Streamlit for a clean, responsive user experience.

## Architecture

The system is built on a graph-based agent workflow:

1. **Research Node**: Gathers market data and news.
2. **Analyst Node**: Synthesizes data into a final report.
3. **Cache Maintenance Node**: Asynchronously cleans up expired news summaries after analysis.

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd StockPlanner
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   # Optional: LANGSMITH_API_KEY for tracing
   ```

## Usage

**Run the Streamlit App:**

```bash
streamlit run src/web/app.py
```

Navigate to `http://localhost:8501` in your browser.

## Project Structure

- `src/agents/`: Definitions for the Research and Analyst agents and the LangGraph workflow.
- `src/tools/`: Market data tools (`market.py`) utilizing `yfinance` and web scraping.
- `src/database/`: SQLite database models and CRUD operations for transaction tracking and caching.
- `src/web/`: Streamlit web application interface.

## Recent Updates

- **Database Caching**: Implemented a unified research cache to store SEC filings, news summaries, and social sentiment, improving speed and efficiency.
- **Robust News Fetching**: Enhanced news gathering with `readability-lxml` and better error handling.

## Roadmap

- Milestone 1: API Server
  - Convert this app into an API server that has the following APIs:
    - `/chat`: Chat endpoint that uses LangGraph Streaming Schema
    - `/investment`: GET endpoints for fetching user's investment portfolio out of user's transactions
    - `/investment/transactions/{transaction_id}`: CRUD endpoints for investment transactions
  - Use Railway PostgreSQL as the cloud database
  - Implement proper long-term memory (PostgreSQL) to store user's portfolio
  - Refactor all documentations
- Milestone 2: Authentication
  - Implement proper Google Sign-in, and auth APIs
  - Implement proper authentication and authorization for each API transaction
  - Update DB schema to separate user's data
- Milestone 3: Chat History
  - Implement proper short-term memory (Redis) to store conversation history
  - Implement storage for user's conversation history
  - Implement APIs for fetching user's conversation history
- Milestone 4: Deep Dive into Agents
  - Break down research and analyst agents into smaller, more specific and independent agents, so that they handle financial and off-topic queries better
  - Implement EDGAR research agent for instituition context
  - Implement social media research agent for social media context
  - Implement sentiment for each news article
  - Implement narrative analysis for the market
  - Break down analyst subagents into its own folder with files, fix any streaming issues
- Milestone 5: Daily AI Analysis
  - Implement deep research agent that scrapes and analyzes news articles
  - Implement daily AI analysis agent that reviews the user's portfolio, deep research news and provides a summary
