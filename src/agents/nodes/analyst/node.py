from src.agents.nodes.analyst.prompts import ANALYST_PROMPT
from src.agents.state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def analyst_node(state: AgentState):
    """
    Analyze the portfolio based on gathered data.
    """
    portfolio = state["portfolio"]
    research_data = state["research_data"]
    macro_economic_news = research_data["macro_economic_news"]
    
    print("--- ANALYZING PORTFOLIO ---")
    
    # Construct prompt
    macro_news = "\n".join([f"- {n.get('title', 'No Title')}: {n.get('summary')}" for n in macro_economic_news if isinstance(n, dict)])
    portfolio_data = ""
    
    for pos in portfolio:
        symbol = pos["symbol"]
        qty = pos["quantity"]
        avg_cost = pos["avg_cost"]
        data = research_data.get(symbol, {})
        
        curr_price = data.get("current_price", 0)
        info = data.get("info") or {}
        news = data.get("news") or []
        
        portfolio_data += f"\n--- {symbol} ---\n"
        portfolio_data += f"Position: {qty} shares @ ${avg_cost:.2f} (Current: ${curr_price:.2f})\n"
        portfolio_data += f"Valuation: PE={info.get('pe_ratio')}, MarketCap={info.get('market_cap')}\n"
        
        if not news:
            portfolio_data += "No news available.\n"
        else:
            portfolio_data += f"News Headlines:\n"
            for n in news[:3]:
                if not isinstance(n, dict): # Add check
                     continue 
                portfolio_data += f"- {n.get('title', 'No Title')}\n"
                portfolio_data += f"  Summary/Excerpt: {n.get('summary', '')[:500]}...\n"
            
    prompt = ANALYST_PROMPT.format(macro_news=macro_news, portfolio=portfolio_data)

    print(prompt)
    
    messages = [
        SystemMessage(content="You are a helpful and insightful senior financial investment analyst, your goal is to analyze the user's portfolio and provide actionable recommendations."),
        HumanMessage(content=prompt)
    ]
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    try:
        response = llm.invoke(messages)
        return {"analysis_report": response.content}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"analysis_report": f"Error running analysis: {e}"}
