from ddgs import DDGS
from typing import Dict, List, Optional
import httpx
from bs4 import BeautifulSoup
import re
from readability import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.database.session import AsyncSessionLocal
from src.graph.utils.prompt import ARTICLE_SUMMARY_PROMPT
from src.services.market_data import get_valid_cache, save_cache

async def get_summary_result(item: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Helper to fetch summary and return a structured result."""
    user_agent = item.get("user_agent", "")
    summary = await get_summary(item['link'], user_agent)
    if summary:
        return {
            "title": item["title"],
            "summary": summary,
            "url": item["link"]
        }
    return None

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

async def get_summary(url: str, user_agent: str = "") -> Optional[str]:
    """
    Get news summary from cache or fetch and summarize.
    TTL: 7 days.
    """
    if not url:
        return None
        
    async with AsyncSessionLocal() as db:
        try:
            # Check cache
            cached_summary = await get_valid_cache(db, url)
            if cached_summary:
                return cached_summary
                
            # Cache miss
            content = await fetch_article_content(url, user_agent)
            if content:
                summary = await summarize_content(content, url)
                if summary and "Error" not in summary:
                    # Use default TTL from save_cache (168 hours / 7 days)
                    await save_cache(db, url, summary)
                    return summary
        except Exception as e:
            print(f"Error in get_summary: {e}")
            
    return None

async def fetch_article_content(url: str, user_agent: str = "") -> Optional[str]:
    """Fetch and extract main text content from a URL."""
    try:
        final_ua = user_agent if user_agent else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"

        headers = {
            "User-Agent": final_ua
        }
        async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            
            # Silently skip any failing responses
            if response.status_code >= 400:
                return None
            
            text_content = response.text
            clean_html = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text_content)
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

async def summarize_content(content: str, url: str) -> Optional[str]:
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
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return None
