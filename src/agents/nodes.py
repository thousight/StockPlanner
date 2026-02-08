import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState
from src.tools.market import get_current_price, get_stock_news, get_company_info, get_macro_economic_news

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
    
    print(f"--- RESEARCHING {len(portfolio)} STOCKS ---")
    
    for pos in portfolio:
        symbol = pos["symbol"]
        print(f"Fetching data for {symbol}...")
        
        research_data[symbol] = {
            "current_price": get_current_price(symbol),
            "news": get_stock_news(symbol),
            "info": get_company_info(symbol)
        }
        
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
    macro_news_text = "\n".join([f"- {n['title']}: {n.get('snippet', 'No snippet')}" for n in macro_economic_news.get('news', [])])
    
    prompt = f"""You are a senior investment analyst.
    Your goal is to analyze the user's portfolio and provide actionable recommendations.

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
        info = data.get("info", {})
        news = data.get("news", [])
        
        prompt += f"\n--- {symbol} ---\n"
        prompt += f"Position: {qty} shares @ ${avg_cost:.2f} (Current: ${curr_price:.2f})\n"
        prompt += f"Valuation: PE={info.get('pe_ratio')}, MarketCap={info.get('market_cap')}\n"
        prompt += f"News Headlines:\n"
        for n in news[:3]:
            prompt += f"- {n.get('title')} ({n.get('snippet', 'No snippet')})\n"
            content = n.get('content', '')
            if content:
                # Add a truncated version of the content to the prompt (first 500 chars)
                # to stay within context limits while giving more info than snippet
                prompt += f"  Summary/Excerpt: {content[:500]}...\n"
            else:
                 prompt += f"  Snippet: {n.get('snippet', 'No details')}\n"
            
    prompt += "\n\nProvide a comprehensive Markdown report."

    print(prompt)
    
    messages = [
        SystemMessage(content="You are a helpful and insightful financial analyst AI."),
        HumanMessage(content=prompt)
    ]
    
    llm = get_llm()
    response = llm.invoke(messages)
    
    return {"analysis_report": response.content}
