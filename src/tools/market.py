import yfinance as yf
from ddgs import DDGS
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import re

def get_current_price(ticker: str) -> float:
    """
    Get the latest market price for a ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        # fast_info is often faster/more reliable for current price than history
        price = stock.fast_info.last_price
        return price
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0

def fetch_article_content(url: str) -> str:
    """
    Fetch and extract main text content from a URL.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit content length to avoid breaking context window
        return text[:500]
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

def get_stock_news(ticker: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for recent news about the stock using DuckDuckGo and fetch content.
    """
    results = []
    try:
        # Check connection or DuckDuckGo status first if possible? 
        # For now just try the query
        query = f"{ticker} stock news market analysis"
        
        # Use a new client for each request to avoid state issues?
        # Or just use the context manager as intended
        with DDGS() as ddgs:
            # text() returns generator
            ddgs_gen = ddgs.text(query, max_results=max_results)
            for r in ddgs_gen:
                # Add fetched content
                url = r.get('href')
                if url:
                    content = fetch_article_content(url)
                    r['content'] = content if content else r.get('body', '')
                results.append(r)
                
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        # Only print detailed error if it is not the common protocol error
        if "0x304" not in str(e):
             print(f"Detailed error: {e}")
             
    return results

def get_company_info(ticker: str) -> Dict[str, Any]:
    """
    Fetch fundamental data and earnings calendar.
    """
    data = {
        "symbol": ticker,
        "sector": "Unknown",
        "market_cap": 0,
        "pe_ratio": None,
        "peg_ratio": None,
        "eps": None,
        "next_earnings": None,
        "analyst_rating": None
    }
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        data["sector"] = info.get("sector", "Unknown")
        data["industry"] = info.get("industry", "Unknown")
        data["market_cap"] = info.get("marketCap", 0)
        data["pe_ratio"] = info.get("trailingPE")
        data["peg_ratio"] = info.get("pegRatio")
        data["eps"] = info.get("trailingEps")
        data["analyst_rating"] = info.get("recommendationKey") # e.g. 'buy', 'hold'

        # Try to get next earnings date (calendar)
        # yfinance calendar is essentially a dict or dataframe
        try:
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                # Calendar format varies, usually has 'Earnings Date' or similar
                # For now, let's try to extract if available
                # It often returns a dict with 'Earnings Date' as a list
                if 'Earnings Date' in calendar:
                    dates = calendar['Earnings Date']
                    if dates:
                        data["next_earnings"] = str(dates[0])
                # alternative structure for some versions
                elif 'Earnings Low' in calendar: # sometimes keys are different
                     pass
        except Exception:
            pass # Calendar fetch often flaky

    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")
        
    return data

def get_macro_economic_news() -> Dict[str, Any]:
    """
    Fetch news about macroeconomics of the day and key market indicators.
    """
    macro_data = {
        "news": [],
        "metrics": {}
    }
    
    # 1. Fetch Key Market Indicators (Proxies for Macro Sentiment)
    # ^GSPC: S&P 500 (General Stock Market)
    # ^VIX: Volatility Index (Fear Gauge)
    # ^TNX: 10-Year Treasury Yield (Interest Rates/Inflation view)
    # DX-Y.NYB: US Dollar Index (Currency Strength)
    tickers = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB"]
    try:
        for ticker in tickers:
             try:
                 t = yf.Ticker(ticker)
                 # fast_info is reliable for current snapshot
                 price = t.fast_info.last_price
                 change = 0.0
                 try:
                     prev = t.fast_info.previous_close
                     if prev:
                         change = ((price - prev) / prev) * 100
                 except:
                     pass
                 
                 macro_data["metrics"][ticker] = {
                     "price": price,
                     "change_percent": change
                 }
             except Exception as fetch_err:
                 print(f"Error for ticker {ticker}: {fetch_err}")
    except Exception as e:
        print(f"Error fetching macro metrics: {e}")

    # 2. Fetch Text News via DuckDuckGo
    queries = [
        "macroeconomics news today",
        "federal reserve interest rates news",
        "inflation cpi report news",
        "US employment report news",
        "Trump social media today",
        "US economy outlook today"
    ]
    
    seen_urls = set()
    
    try:
        with DDGS() as ddgs:
            for q in queries:
                try:
                    # Limit results per query
                    results = ddgs.text(q, max_results=2)
                    for r in results:
                        if r['href'] not in seen_urls:
                            macro_data["news"].append({
                                "title": r['title'],
                                "link": r['href'],
                                "source": "DuckDuckGo",
                                "snippet": r['body']
                            })
                            seen_urls.add(r['href'])
                except Exception as q_err:
                    print(f"Error for query {q}: {q_err}")
    except Exception as e:
        print(f"Error fetching macro news: {e}")
        
    return macro_data
    