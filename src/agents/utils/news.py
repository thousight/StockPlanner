import yfinance as yf
from ddgs import DDGS
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import re
from readability import Document
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.database.database import SessionLocal
from src.database.crud import get_valid_cache, save_cache
from src.agents.utils.prompts import ARTICLE_SUMMARY_PROMPT

def get_stock_news(symbol: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch and summarize the latest news for a specific stock ticker.
    """
    results = []
    try:
        stock = yf.Ticker(symbol)
        news_items = stock.news
        
        if not news_items:
             return []

        for item in news_items[:max_results]:
            parsed = _parse_yf_news_item(item)
            if not parsed:
                continue
                
            result = get_summary_result(parsed)
            if result:
                results.append(result)
                
        return results
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []

def get_macro_economic_news() -> List[Dict[str, Any]]:
    """
    Fetch and summarize the latest global macroeconomic news and indicators.
    """
    title_and_urls = []

    # 1. Collect URLs from yfinance tickers in parallel
    tickers = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB"]
    with ThreadPoolExecutor(max_workers=4) as executor:
        for result in executor.map(fetch_yfinance_news_urls, tickers):
            title_and_urls.extend(result)
    
    # 2. Collect URLs from DuckDuckGo queries in parallel
    queries = [
        "Macroeconomics news today",
        "US economy outlook today",
        "Federal Reserve interest rates news",
        "US employment report news",
        "US inflation cpi report news",
    ]
    with ThreadPoolExecutor(max_workers=5) as executor:
        for result in executor.map(fetch_ddgs_urls, queries):
            title_and_urls.extend(result)
            
    # 3. Deduplicate by URL
    seen_urls = set()
    unique_candidates = []
    for item in title_and_urls:
        if item["link"] not in seen_urls:
            unique_candidates.append(item)
            seen_urls.add(item["link"])
            
    # 4. Fetch summaries in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_results = list(executor.map(get_summary_result, unique_candidates))
        
    return [r for r in all_results if r]


def web_search(queries: List[str]) -> List[List[Dict[str, str]]]:
    """
    Perform web search and get title and page summary by the queries.
    Returns a list of results, where each outer index corresponds to the query index,
    and the inner list contains the summarized results for that query.
    """
    # 1. Fetch URLs for each query in parallel
    # list(executor.map) returns results in the exact same order as the input queries
    with ThreadPoolExecutor(max_workers=5) as executor:
        query_results = list(executor.map(fetch_ddgs_urls, queries))
    
    # 2. Collect unique candidate URLs to speed up summary extraction
    unique_candidates = {}
    for items in query_results:
        for item in items:
            link = item.get("link")
            if link and link not in unique_candidates:
                unique_candidates[link] = item
                
    # 3. Fetch summaries in parallel for unique candidates
    candidate_list = list(unique_candidates.values())
    with ThreadPoolExecutor(max_workers=5) as executor:
        summarized_results = list(executor.map(get_summary_result, candidate_list))
        
    # Create a lookup mapping from URL to the summarized result
    summary_map = {}
    for res in summarized_results:
        if res and "url" in res:
            summary_map[res["url"]] = res
            
    # 4. Rebuild the final results grouped by query
    final_results = []
    for items in query_results:
        query_group = []
        seen_in_group = set()
        for item in items:
            link = item.get("link")
            # Ensure we have a valid summary and prevent exact duplicates per query
            if link and link in summary_map and link not in seen_in_group:
                query_group.append(summary_map[link])
                seen_in_group.add(link)
        final_results.append(query_group)
        
    return final_results

def get_summary_result(item: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Helper to fetch summary and return a structured result."""
    summary = get_summary(item['link'])
    if summary:
        return {
            "title": item["title"],
            "summary": summary,
            "url": item["link"]
        }
    return None

def fetch_yfinance_news_urls(ticker: str) -> List[Dict[str, str]]:
    """Fetch news URLs for a single ticker."""
    results = []
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news
        if news_items:
            for item in news_items:
                parsed = _parse_yf_news_item(item)
                if parsed:
                    results.append(parsed)
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
    return results

def fetch_ddgs_urls(query: str) -> List[Dict[str, str]]:
    """Fetch news URLs for a single query."""
    results = []
    try:
        with DDGS() as ddgs:
            items = ddgs.text(query, max_results=2)
            for r in items:
                link = r.get('href')
                if link:
                    results.append({
                        "title": r.get('title', 'No Title'),
                        "link": link,
                    })
    except Exception as e:
        print(f"Error for query {query}: {e}")
    return results

def get_summary(url: str) -> Optional[str]:
    """
    Get news summary from cache or fetch and summarize.
    TTL: 7 days.
    """
    if not url:
        return None
        
    db = SessionLocal()
    try:
        # Check cache
        cached_summary = get_valid_cache(db, url)
        if cached_summary:
            return cached_summary
            
        # Cache miss
        content = fetch_article_content(url)
        if content:
            summary = summarize_content(content, url)
            if summary and "Error" not in summary:
                # 7-day TTL
                expire_at = datetime.utcnow() + timedelta(days=7)
                save_cache(db, url, summary, expire_at)
                return summary
    except Exception as e:
        print(f"Error in get_summary: {e}")
    finally:
        db.close()
        
    return None

def fetch_article_content(url: str) -> str:
    """Fetch and extract main text content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        clean_html = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', response.text)
        doc = Document(clean_html)
        html_content = doc.summary()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        if text:
            text = str(text)
            text = re.sub(r'\s+', ' ', text).strip()
        else:
            text = "No readable text found."
        return text
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

def summarize_content(content: str, url: str) -> str:
    """Summarize content using an LLM."""
    if not content or len(content) < 100:
        return None
        
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        prompt = ARTICLE_SUMMARY_PROMPT.format(content=content[:4000])
        messages = [
            SystemMessage(content="You are a helpful financial research assistant."),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return "Error generating summary."

def _parse_yf_news_item(item: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Parse a yfinance news item."""
    try:
        if 'content' in item:
            content = item['content']
            title = content.get('title')
            link = None
            if 'clickThroughUrl' in content and content['clickThroughUrl']:
                link = content['clickThroughUrl'].get('url')
            if not link and 'canonicalUrl' in content and content['canonicalUrl']:
                link = content['canonicalUrl'].get('url')
            if title and link:
                return {"title": title, "link": link}
        elif 'title' in item and 'link' in item:
            return {
                "title": item.get('title'),
                "link": item.get('link'),
            }
    except Exception as e:
        print(f"Error parsing news item: {e}")
    return None
