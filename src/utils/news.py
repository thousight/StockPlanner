import os
import yfinance as yf
from ddgs import DDGS
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import re
from readability import Document
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.database.database import SessionLocal
from src.database.crud import get_valid_cache, save_cache
from src.utils.prompt import ARTICLE_SUMMARY_PROMPT

def get_summary_result(item: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Helper to fetch summary and return a structured result."""
    user_agent = item.get("user_agent", "")
    summary = get_summary(item['link'], user_agent)
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

def get_summary(url: str, user_agent: str = "") -> Optional[str]:
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
        content = fetch_article_content(url, user_agent)
        if content:
            summary = summarize_content(content, url)
            if summary and "Error" not in summary:
                # Use default TTL from save_cache (168 hours / 7 days)
                save_cache(db, url, summary)
                return summary
    except Exception as e:
        print(f"Error in get_summary: {e}")
    finally:
        db.close()
        
    return None

def fetch_article_content(url: str, user_agent: str = "") -> str:
    """Fetch and extract main text content from a URL."""
    try:
        final_ua = user_agent if user_agent else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"

        headers = {
            "User-Agent": final_ua
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Silently skip any failing responses
        if response.status_code >= 400:
            return None
        
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
    except Exception:
        # Silently skip any connection errors, parsing errors, etc.
        return None

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
        return None

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
