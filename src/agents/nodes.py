from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from concurrent.futures import ThreadPoolExecutor
from src.agents.state import AgentState
from src.tools.market import resolve_symbol, get_macro_economic_news
from src.database.database import SessionLocal
from src.database.crud import cleanup_expired_cache

# Initialize LLM lazily
def get_llm():
    return ChatOpenAI(model="gpt-4o", temperature=0)

def research_node(state: AgentState):
    """
    Gather data for all stocks in the portfolio.
    """
    portfolio = state["portfolio"]
    research_data = {}

    research_data["macro_economic_news"] = get_macro_economic_news()
    
    # Fetch portfolio data in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_symbol_data, portfolio))
    
    for symbol, data in results:
        research_data[symbol] = data
        
    return {"research_data": research_data}

def analyst_node(state: AgentState):
    """
    Analyze the portfolio based on gathered data.
    """
    portfolio = state["portfolio"]
    research_data = state["research_data"]
    macro_economic_news = research_data["macro_economic_news"]
    
    print("--- ANALYZING PORTFOLIO ---")
    
    # Construct prompt
    macro_news_text = "\n".join([f"- {n.get('title', 'No Title')}: {n.get('summary')}" for n in macro_economic_news if isinstance(n, dict)])
    
    prompt = f"""You are a senior investment analyst, your goal is to analyze the user's portfolio and provide actionable recommendations.

First, summarize and analyze the macro economic news of the day:
{macro_news_text}
    
Then, for each stock in the portfolio, analyze:
1. Valuation (PE ratio, comparison to sector if known)
2. Recent News Sentiment and how they can impact each stocks
3. Earnings Outlook (if data available)
4. Performance (Current Price vs Avg Cost)

Finally, provide a "Buy", "Sell", or "Hold" recommendation with reasoning.

Portfolio Data:
"""
    
    for pos in portfolio:
        symbol = pos["symbol"]
        qty = pos["quantity"]
        avg_cost = pos["avg_cost"]
        data = research_data.get(symbol, {})
        
        curr_price = data.get("current_price", 0)
        info = data.get("info") or {}
        news = data.get("news") or []
        
        prompt += f"\n--- {symbol} ---\n"
        prompt += f"Position: {qty} shares @ ${avg_cost:.2f} (Current: ${curr_price:.2f})\n"
        prompt += f"Valuation: PE={info.get('pe_ratio')}, MarketCap={info.get('market_cap')}\n"
        
        if not news:
            prompt += "No news available.\n"
        else:
            prompt += f"News Headlines:\n"
            for n in news[:3]:
                if not isinstance(n, dict): # Add check
                     continue 
                prompt += f"- {n.get('title', 'No Title')}\n"
                prompt += f"  Summary/Excerpt: {n.get('summary', '')[:500]}...\n"
            
    prompt += "\n\nProvide a comprehensive Markdown report."

    print(prompt)
    
    messages = [
        SystemMessage(content="You are a helpful and insightful financial analyst AI."),
        HumanMessage(content=prompt)
    ]
    
    llm = get_llm()
    try:
        response = llm.invoke(messages)
        return {"analysis_report": response.content}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"analysis_report": f"Error running analysis: {e}"}

def cache_maintenance_node(state: AgentState):
    """
    Clean up expired news cache entries.
    """
    print("--- CACHE MAINTENANCE ---")
    try:
        db = SessionLocal()
        cleanup_expired_cache(db)
        db.close()
    except Exception as e:
        print(f"Error in cache maintenance: {e}")
        
    return state

def fetch_symbol_data(pos):
    symbol = pos["symbol"]
    print(f"Fetching data for {symbol}...")
    return (symbol, resolve_symbol(symbol))