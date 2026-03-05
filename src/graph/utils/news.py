from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from ddgs import DDGS
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.database.session import AsyncSessionLocal
from src.database.models import ResearchCache, ResearchSourceType
from src.graph.utils.prompt import ARTICLE_SUMMARY_PROMPT
from src.graph.utils.scraping import fetch_content, clean_html, DEFAULT_USER_AGENT

async def get_summary_result(item: Dict[str, str], expire_at: Optional[datetime] = None) -> Optional[Dict[str, str]]:
    """Helper to fetch summary and return a structured result."""
    user_agent = item.get("user_agent", "")
    summary = await get_summary(item['link'], user_agent, expire_at=expire_at)
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

async def get_summary(url: str, user_agent: str = "", expire_at: Optional[datetime] = None) -> Optional[str]:
    """
    Get news summary from cache or fetch and summarize.
    TTL: Default 7 days if expire_at not provided.
    """
    if not url:
        return None
        
    async with AsyncSessionLocal() as db:
        try:
            # 1. Check unified ResearchCache
            stmt = select(ResearchCache).where(
                ResearchCache.key == url,
                ResearchCache.expire_at > datetime.now(timezone.utc).replace(tzinfo=None)
            )
            result = await db.execute(stmt)
            cached = result.scalar_one_or_none()
            if cached:
                return cached.content
                
            # 2. Cache miss - Fetch and Summarize
            ua = user_agent if user_agent else DEFAULT_USER_AGENT
            html = await fetch_content(url, ua)
            if html:
                content = clean_html(html)
                if content:
                    summary = await summarize_content(content, url)
                    if summary and "Error" not in summary:
                        # Save to unified ResearchCache
                        if expire_at is None:
                            expire_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
                        
                        new_cache = ResearchCache(
                            source_type=ResearchSourceType.NEWS,
                            key=url,
                            content=summary,
                            expire_at=expire_at
                        )
                        db.add(new_cache)
                        await db.commit()
                        return summary
        except Exception as e:
            print(f"Error in get_summary: {e}")
            
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
