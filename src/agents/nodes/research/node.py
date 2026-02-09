from concurrent.futures import ThreadPoolExecutor
from src.agents.state import AgentState
from src.agents.nodes.research.utils import get_macro_economic_news, resolve_symbol

def research_node(state: AgentState):
    """
    Gather data for all stocks in the portfolio.
    """
    holdings = state["portfolio"]
    research_data = {}

    research_data["macro_economic_news"] = get_macro_economic_news()
    
    # Fetch portfolio data in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_symbol_data, holdings))
    
    for symbol, data in results:
        research_data[symbol] = data
        
    return {"research_data": research_data}

def fetch_symbol_data(holding):
    symbol = holding["symbol"]
    return (symbol, resolve_symbol(symbol))