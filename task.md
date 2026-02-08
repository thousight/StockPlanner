# Stock Analysis Application - Task List

## Phase 1: MVP (Local Loop)
**Goal**: Single-user local app with Portfolio CRUD, Market Data, and Basic Analysis Agents.

- [/] **Infrastructure & Setup**
    - [x] Initialize git and project structure
    - [x] Setup `requirements.txt` (Streamlit, LangChain, yfinance, SQLAlchemy)
    - [x] Fix module import issues (IDE configuration)
    - [x] Fix Streamlit import error (IDE configuration)
    - [x] Configure environment variables (.env)
- [/] **Data Layer (SQLite)**
    - [x] Implement Models: `Portfolio`, `Stock`, `Transaction`, `DailySnapshot`
    - [ ] Implement CRUD Services: `PortfolioService`, `TransactionService`
- [ ] **Market Data & Research Tools**
    - [ ] Implement `PriceFetcher` (yfinance)
    - [ ] Implement `NewsFetcher` (DuckDuckGo/Search API)
    - [ ] Implement `FundamentalFetcher` (yfinance: Balance Sheet, Income Stmt, Earnings Dates)
- [ ] **Agentic Workflow (LangGraph)**
    - [ ] Create `ResearchAgent`: Gathers news and data
    - [ ] Create `AnalystAgent`: Summarizes and suggests based on simple prompts
    - [ ] Define Graph: Data -> Research -> Analysis -> Output
- [ ] **User Interface (Streamlit)**
    - [ ] **Portfolio Page**: List holdings, Add/Edit Transactions, View Performance
    - [ ] **Analysis Page**: Trigger Agent Run, View Markdown Report
