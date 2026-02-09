import yfinance as yf
from ddgs import DDGS
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import re
from readability import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.database.database import SessionLocal
from src.database.crud import get_valid_cache, save_cache

def resolve_symbol(symbol: str) -> str:
    """
    Resolve the symbol to its actual ticker.
    """
    try:
        stock = yf.Ticker(symbol)
        return {
            "current_price": get_current_price(stock),
            "news": get_stock_news(stock),
            "info": get_company_info(stock)
        }
    except Exception as e:
        print(f"Error resolving symbol for {symbol}: {e}")
        return symbol

def get_current_price(stock: yf.Ticker) -> float:
    """
    Get the latest market price for a ticker.
    """
    try:
        # fast_info is often faster/more reliable for current price than history
        return stock.fast_info.last_price
    except Exception as e:
        print(f"Error fetching price for {stock.ticker}: {e}")
        return 0.0

def get_company_info(stock: yf.Ticker) -> Dict[str, Any]:
    """
    Fetch fundamental data and earnings calendar.
    """
    data = {
        "symbol": stock.ticker,
        "sector": "Unknown",
        "market_cap": 0,
        "pe_ratio": None,
        "peg_ratio": None,
        "eps": None,
        "next_earnings": None,
        "analyst_rating": None
    }
    
    try:
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
        print(f"Error fetching fundamentals for {stock.ticker}: {e}")
        
    return data

def get_stock_news(stock: yf.Ticker, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search for recent news about the stock using Yahoo Finance and summarize content.
    """
    results = []
    try:
        # print(f"DEBUG: Fetching stock news for {stock.ticker} via yfinance...")
        news_items = stock.news
        
        # Handle case where stock.news returns None or empty
        if not news_items:
             print(f"DEBUG: No news found for {stock.ticker}")
             return []

        for item in news_items[:max_results]:
            parsed = _parse_yf_news_item(item)
            if not parsed:
                continue
                
            title = parsed['title']
            link = parsed['link']
            publisher = parsed['publisher']
            
            summary = get_news_summary(link)

            if summary:
                results.append({
                    "title": title,
                    "link": link,
                    "source": publisher,
                    "summary": summary
                })
                
            return results
    except Exception as e:
        print(f"Error fetching news for {stock.ticker}: {e}")

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

    # 2. Fetch Text News
    # Hybrid Approach: yfinance for indices, DDGS for specific topics
    
    seen_urls = set() # Initialize seen_urls here for both sections

    # A. Index News from yfinance
    # We use the same tickers as metrics
    for ticker in tickers:
        try:
             stock = yf.Ticker(ticker)
             news_items = stock.news
             if news_items:
                 # Get top 1 news item for each index
                 item = news_items[0]
                 parsed = _parse_yf_news_item(item)
                 
                 if parsed:
                     link = parsed['link']
                     title = parsed['title']
                     summary = "No content fetched."
                     if link and link not in seen_urls:
                         summary = get_news_summary(link)
                        
                         if summary:
                             macro_data["news"].append({
                                 "title": title,
                                 "link": link,
                                 "source": f"yfinance ({ticker})",
                                 "summary": summary
                             })
                             seen_urls.add(link)
        except Exception as e:
            print(f"Error fetching macro news for {ticker}: {e}")

    # B. Specific Topic News via DuckDuckGo
    # Reduced list since we get general market news from indices
    queries = [
        "macroeconomics news today",
        "federal reserve interest rates news",
        "US economy outlook today"
        "Trump social media today",
        "US employment report news",
        "US employment report"
        "inflation cpi report news",
        "US inflation report",
    ]
    
    try:
        with DDGS() as ddgs:
            for q in queries:
                try:
                    # Limit results per query
                    results = ddgs.text(q, max_results=1)
                    # print(f"DEBUG: Found {len(results)} results for query: {q}")
                    for r in results:
                        link = r['href']
                        if link and link not in seen_urls:
                            # Fetch and summarize
                            summary = get_news_summary(link)
                                
                            if summary:
                                macro_data["news"].append({
                                    "title": r['title'],
                                    "link": link,
                                    "source": "DuckDuckGo",
                                    "summary": summary
                                })
                            seen_urls.add(link)
                except Exception as q_err:
                    print(f"Error for query {q}: {q_err}")
    except Exception as e:
        print(f"Error fetching macro news: {e}")
        
    return macro_data

def get_news_summary(url: str) -> Optional[str]:
    """
    Get news summary from cache or fetch and summarize.
    """
    if not url:
        return None
        
    db = SessionLocal()
    try:
        # Check cache
        cached_summary = get_valid_cache(db, url)
        if cached_summary:
            # print(f"DEBUG: Cache hit for {url}")
            return cached_summary
            
        # Cache miss
        # print(f"DEBUG: Cache miss for {url}, fetching...")
        content = fetch_article_content(url)
        if content:
            summary = summarize_content(content, url)
            if summary and "Error" not in summary:
                save_cache(db, url, summary)
                return summary
    except Exception as e:
        print(f"Error in get_news_summary: {e}")
    finally:
        db.close()
        
    return None

def fetch_article_content(url: str) -> str:
    """
    Fetch and extract main text content from a URL using readability-lxml.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Sanitize text to avoid lxml issues with control characters
        clean_html = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', response.text)
        
        doc = Document(clean_html)
        html_content = doc.summary()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up text
        if text:
            text = str(text)
            text = re.sub(r'\s+', ' ', text).strip()
        else:
            text = "No readable text found."
        
        # print(f"DEBUG: Successfully fetched {len(text)} chars from {url}")
        return text
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

def summarize_content(content: str, url: str) -> str:
    """
    Summarize the key financial insights from the article content using an LLM.
    """
    if not content or len(content) < 100:
        return None
        
    try:
        # print(f"DEBUG: Summarizing content from {url}...")
        llm = ChatOpenAI(model="gpt-4o")
        
        prompt = f"""
        Summarize the key financial insights from the following article. 
        Focus on information relevant to stock analysis, market trends, and economic indicators.
        Keep the summary concise (2-3 sentences).
        
        Article Content:
        {content[:4000]}
        """
        
        messages = [
            SystemMessage(content="You are a helpful financial research assistant."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        summary = response.content.strip()
        # print(f"DEBUG: Generated summary: {summary[:50]}...")
        return summary
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return "Error generating summary."

def _parse_yf_news_item(item: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Parse a yfinance news item which might vary in structure.
    Returns dict with title, link, publisher, or None if invalid.
    """
    try:
        # Check for nested 'content' structure (new yfinance)
        if 'content' in item:
            content = item['content']
            title = content.get('title')
            
            # Try to find link in clickThroughUrl or canonicalUrl
            link = None
            if 'clickThroughUrl' in content and content['clickThroughUrl']:
                link = content['clickThroughUrl'].get('url')
            if not link and 'canonicalUrl' in content and content['canonicalUrl']:
                link = content['canonicalUrl'].get('url')
                
            publisher = "Yahoo Finance"
            if 'provider' in content:
                publisher = content['provider'].get('displayName', "Yahoo Finance")
                
            if title and link:
                return {"title": title, "link": link, "publisher": publisher}
                
        # Fallback to flat structure (old yfinance)
        elif 'title' in item and 'link' in item:
            return {
                "title": item.get('title'),
                "link": item.get('link'),
                "publisher": item.get('publisher', 'Unknown')
            }
            
    except Exception as e:
        print(f"Error parsing news item: {e}")
        
    return None
