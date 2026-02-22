import yfinance as yf
from typing import Dict, Any

def get_stock_financials(symbol: str) -> Dict[str, Any]:
    """
    Fetch fundamental financial data (PE, Market Cap, EPS, etc.) for a specific ticker.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        data = {
            "symbol": symbol,
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE"),
            "peg_ratio": info.get("pegRatio"),
            "eps": info.get("trailingEps"),
            "analyst_rating": info.get("recommendationKey"),
            "current_price": stock.fast_info.last_price if hasattr(stock, 'fast_info') else 0.0
        }
        
        # Try to get next earnings date
        try:
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                if 'Earnings Date' in calendar:
                    dates = calendar['Earnings Date']
                    if dates:
                        data["next_earnings"] = str(dates[0])
        except Exception:
            pass
            
        return data
    except Exception as e:
        print(f"Error fetching financials for {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}

def get_current_price(symbol: str) -> float:
    """
    Get the latest market price for a ticker.
    """
    try:
        stock = yf.Ticker(symbol)
        return stock.fast_info.last_price
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return 0.0
