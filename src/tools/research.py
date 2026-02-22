import yfinance as yf

def get_stock_financials(symbol: str) -> str:
    """
    Fetch fundamental financial data (PE, Market Cap, EPS, etc.) for a specific ticker.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Build markdown bulleted string
        md_lines = [f"**Financial Data for {symbol}**"]
        
        pe_ratio = info.get("trailingPE", "N/A")
        market_cap = info.get("marketCap", "N/A")
        if market_cap != "N/A":
            market_cap = f"${market_cap:,.0f}"
        eps = info.get("trailingEps", "N/A")
        revenue = info.get("totalRevenue", "N/A")
        if revenue != "N/A":
            revenue = f"${revenue:,.0f}"
        profit_margin = info.get("profitMargins", "N/A")
        if profit_margin != "N/A":
            profit_margin = f"{profit_margin * 100:.2f}%"
            
        md_lines.append(f"- Market Cap: {market_cap}")
        md_lines.append(f"- P/E Ratio: {pe_ratio}")
        md_lines.append(f"- EPS: {eps}")
        md_lines.append(f"- Total Revenue: {revenue}")
        md_lines.append(f"- Profit Margin: {profit_margin}")
        
        business_summary = info.get("longBusinessSummary", "N/A")
        if business_summary != "N/A":
            md_lines.append(f"- Business Summary: {business_summary}")
        
        return "\n".join(md_lines)
    except Exception as e:
        return f"Failed to fetch financial data for {symbol}: {e}"
