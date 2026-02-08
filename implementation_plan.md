# Implementation Plan - Phase 1: MVP

## Goal
Build a local, single-user Stock Analysis MVP that allows tracking a portfolio and receiving AI-driven analysis and suggestions.

## User Review Required
> [!NOTE]
> **Authentication Removed**: Per Phase 1 requirements, we are stripping Google Auth. The app will run locally and assume a single user (or no user login required yet).
> **Data Persistence**: We will use a local SQLite database (`stocks.db`).

## Proposed Changes

### 1. Infrastructure
Standard Python structure. No complex cloud config yet.

#### [NEW] [requirements.txt](file:///Users/marwen/Projects/StockPlanner/requirements.txt)
- `streamlit`: UI
- `langchain`, `langgraph`, `langchain-openai`: Agents
- `yfinance`: Market Data
- `duckduckgo-search`: News
- `sqlalchemy`: DB ORM
- `pydantic`: Validation

### 2. Data Layer (SQLite)
We need robust tracking of transactions to calculate cost basis and performance.

#### [NEW] [src/database/models.py](file:///Users/marwen/Projects/StockPlanner/src/database/models.py)
- `Portfolio`: (Simple wrapper for now, optional if single user)
- `Stock`: Ticker, Name, Sector.
- `Transaction`:
    - `id`, `date`, `ticker`, `action` (BUY/SELL), `quantity`, `price_per_share`, `fees`.
- `DailySnapshot`: To track portfolio value history.

#### [NEW] [src/database/crud.py](file:///Users/marwen/Projects/StockPlanner/src/database/crud.py)
- `add_transaction(...)`
- `get_holdings(...)`: Calculates current quantity and average cost per stock based on transaction history.
- `get_portfolio_value(...)`

### 3. Core Logic & Agents

#### [NEW] [src/tools/market.py](file:///Users/marwen/Projects/StockPlanner/src/tools/market.py)
- `get_current_price(ticker)`
- `get_stock_news(ticker)`: Uses DuckDuckGo to find recent news.
- `get_company_info(ticker)`: Uses `yfinance`.
    - **Fundamentals**: Market Cap, PE Ratio, EPS, Sector.
    - **Financials**: Balance Sheet bits (Cash, Debt) if needed.
    - **Calendar**: Next Earnings Date.

#### [NEW] [src/agents/analyst.py](file:///Users/marwen/Projects/StockPlanner/src/agents/analyst.py)
- **Role**: Analyze a specific stock or the whole portfolio.
- **Workflow**:
    1. **Input**: List of holdings (Ticker, Qty, Avg Cost, Current Price).
    2. **Research**: Loop, for each stock -> fetch news & price action.
    3. **Synthesize**: LLM considers news + performance.
    4. **Recommendation**: "Buy/Sell/Hold" with reasoning.

### 4. User Interface (Streamlit)

#### [NEW] [src/web/app.py](file:///Users/marwen/Projects/StockPlanner/src/web/app.py)
- **Home**: Dashboard showing Total Portfolio Value (Live).
- **Manage**: Form to Add Transactions. Table of current holdings.
- **Analysis**: Button "Running Daily Analysis". Displays text stream of agent thought process -> Final Markdown Report.

## Verification Plan
1. **Setup**: Install deps.
2. **Data Entry**: Add a "Buy" transaction for AAPL (10 shares @ $150).
3. **Calculation Check**: Verify UI shows 10 shares, Cost Basis $1500.
4. **Agent Run**: Run analysis. Verify it finds *current* AAPL news and mentions the price difference (e.g. "AAPL is now $200, you are up...").
