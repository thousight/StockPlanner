from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from src.graph.utils.prompt import FINANCIAL_SENTIMENT_PROMPT
from src.graph.tools.news import get_stock_news, fetch_ddgs_urls
from src.graph.tools.sec import get_sec_filing_section
from src.services.social import x_client
import asyncio

from src.database.session import AsyncSessionLocal
from src.database.models import ResearchCache, ResearchSourceType
from sqlalchemy import select
from datetime import datetime, timezone, timedelta

class SentimentResult(BaseModel):
    sentiment_score: float = Field(description="Sentiment score from -1.0 to 1.0")
    rationale: str = Field(description="Concise reason for the score")

async def analyze_sentiment(text: str, source_type: ResearchSourceType = ResearchSourceType.NEWS, ticker: Optional[str] = None, key: Optional[str] = None) -> SentimentResult:
    """
    Analyze the sentiment of a given financial text.
    Uses ResearchCache to avoid redundant LLM calls.
    """
    if not text or len(text.strip()) < 20:
        return SentimentResult(sentiment_score=0.0, rationale="Insufficient text for analysis.")

    # 1. Check Cache if key provided
    if key:
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(ResearchCache).where(
                    ResearchCache.key == key,
                    ResearchCache.expire_at > datetime.now(timezone.utc).replace(tzinfo=None)
                )
                result = await db.execute(stmt)
                cached = result.scalar_one_or_none()
                if cached and cached.sentiment_score is not None:
                    return SentimentResult(
                        sentiment_score=float(cached.sentiment_score),
                        rationale=cached.sentiment_reason
                    )
            except Exception as e:
                print(f"Cache check error in analyze_sentiment: {e}")

    # 2. Analyze with LLM
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        structured_llm = llm.with_structured_output(SentimentResult)
        
        # Simple truncation for token limits
        res = await structured_llm.ainvoke(
            FINANCIAL_SENTIMENT_PROMPT.format(text=text[:8000])
        )
        
        # 3. Update Cache if key provided
        if key:
            async with AsyncSessionLocal() as db:
                try:
                    stmt = select(ResearchCache).where(ResearchCache.key == key)
                    result = await db.execute(stmt)
                    cached = result.scalar_one_or_none()
                    
                    ttl_days = 1 if source_type in [ResearchSourceType.SOCIAL, ResearchSourceType.X] else 7
                    expire_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=ttl_days)

                    if cached:
                        cached.sentiment_score = res.sentiment_score
                        cached.sentiment_reason = res.rationale
                        cached.expire_at = expire_at
                    else:
                        new_cache = ResearchCache(
                            source_type=source_type,
                            ticker=ticker,
                            key=key,
                            content=text[:1000], # Store a snippet if needed
                            sentiment_score=res.sentiment_score,
                            sentiment_reason=res.rationale,
                            expire_at=expire_at
                        )
                        db.add(new_cache)
                    await db.commit()
                except Exception as e:
                    print(f"Cache update error in analyze_sentiment: {e}")
                
        return res
    except Exception as e:
        print(f"Error in analyze_sentiment: {e}")
        return SentimentResult(sentiment_score=0.0, rationale=f"Analysis failed: {str(e)}")

async def get_market_sentiment(ticker: str, **kwargs) -> str:
    """
    Aggregate sentiment from News, SEC, and Social (X/Reddit) for a given ticker.
    Returns a weighted sentiment analysis.
    """
    # 1. Fetch data from multiple sources in parallel
    tasks = [
        get_stock_news(ticker, max_results=3, **kwargs),
        get_sec_filing_section(ticker, filing_type="10-K", section_id="item1a"),
        x_client.get_recent_cashtag_tweets(ticker, max_results=5),
        asyncio.to_thread(fetch_ddgs_urls, f"site:reddit.com/r/wallstreetbets ${ticker}")
    ]
    
    results = await asyncio.gather(*tasks)
    news_data, sec_data, x_tweets, reddit_data = results

    # 2. Analyze sentiment for each source
    sentiment_tasks = []
    
    # News sentiment
    if news_data:
        sentiment_tasks.append(analyze_sentiment(news_data, ResearchSourceType.NEWS, ticker, f"news_{ticker}"))
    else:
        sentiment_tasks.append(asyncio.sleep(0, result=None))

    # SEC sentiment
    if sec_data and "Error" not in sec_data:
        sentiment_tasks.append(analyze_sentiment(sec_data, ResearchSourceType.SEC, ticker, f"sec_{ticker}_item1a"))
    else:
        sentiment_tasks.append(asyncio.sleep(0, result=None))

    # X (Social) sentiment
    if x_tweets:
        combined_tweets = "\n".join([t['text'] for t in x_tweets])
        current_hour = datetime.now(timezone.utc).strftime("%Y%m%d%H")
        sentiment_tasks.append(analyze_sentiment(combined_tweets, ResearchSourceType.X, ticker, f"x_{ticker}_{current_hour}"))
    else:
        sentiment_tasks.append(asyncio.sleep(0, result=None))

    # Reddit (Social) sentiment
    if reddit_data:
        combined_reddit = "\n".join([r['title'] for r in reddit_data])
        current_hour = datetime.now(timezone.utc).strftime("%Y%m%d%H")
        sentiment_tasks.append(analyze_sentiment(combined_reddit, ResearchSourceType.SOCIAL, ticker, f"reddit_{ticker}_{current_hour}"))
    else:
        sentiment_tasks.append(asyncio.sleep(0, result=None))

    sentiment_results = await asyncio.gather(*sentiment_tasks)
    
    # 3. Aggregate and weight
    # Weights: SEC (0.4), News (0.3), X (0.15), Reddit (0.15)
    weights = [0.3, 0.4, 0.15, 0.15]
    total_score = 0.0
    total_weight = 0.0
    source_names = ["News", "SEC", "X (Social)", "Reddit (Social)"]
    breakdown = []

    for i, res in enumerate(sentiment_results):
        if res:
            total_score += res.sentiment_score * weights[i]
            total_weight += weights[i]
            breakdown.append(f"- **{source_names[i]}**: {res.sentiment_score} ({res.rationale})")

    final_score = total_score / total_weight if total_weight > 0 else 0.0
    
    output = [
        f"### Market Sentiment for {ticker}",
        f"**Aggregate Score: {final_score:.2f}**",
        "\nSource Breakdown:",
        "\n".join(breakdown) if breakdown else "- No data available for sentiment analysis."
    ]
    
    return "\n".join(output) + "\n"
