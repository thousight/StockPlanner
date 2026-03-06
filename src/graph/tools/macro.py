import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from sqlalchemy import select

from src.database.session import AsyncSessionLocal
from src.database.models import ResearchCache, ResearchSourceType
from src.services.macro import fed_service, calendar_service
from src.graph.tools.sentiment import analyze_sentiment
from src.services.social import x_client

def format_series(name: str, data: List[Dict[str, str]], unit: str) -> str:
    """Helper to format FRED series data for the report."""
    if not data:
        return f"- **{name}:** Data unavailable."
    
    latest = data[0]
    line = f"- **{name}:** {latest['value']} {unit} (as of {latest['date']})"
    
    if len(data) > 1:
        previous = data[1]
        line += f" | Previous: {previous['value']} (as of {previous['date']})"
        
    return line

async def get_political_sentiment(**kwargs) -> str:
    """
    Monitor and analyze the latest political sentiment from key figures (e.g., Trump's X account).
    """
    username = "realDonaldTrump"
    tweets = await x_client.get_user_tweets(username, max_results=5)
    
    if not tweets:
        return f"No recent updates found for @{username}."
        
    combined_text = "\n".join([t['text'] for t in tweets])
    
    # Analyze sentiment
    sentiment = await analyze_sentiment(
        combined_text, 
        source_type=ResearchSourceType.X,
        key=f"political_{username}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}"
    )
    
    output = [f"### Political Sentiment Monitoring (@{username})"]
    output.append(f"**Sentiment Score: {sentiment.sentiment_score:.2f}**")
    output.append(f"**Rationale:** {sentiment.rationale}")
    output.append("\nRecent Updates:")
    for t in tweets:
        output.append(f"- {t['text']} (Likes: {t['metrics'].get('like_count', 0)})")
        
    return "\n".join(output) + "\n"

async def get_key_macro_indicators(**kwargs) -> str:
    """
    Fetch the latest key US macroeconomic indicators (GDP, CPI, Payrolls, Interest Rates, DXY) 
    and upcoming high-impact economic events.
    
    Implements tool-level caching with daily reset (macro_YYYYMMDD).
    """
    # 1. Check Cache
    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    cache_key = f"macro_{today_str}"
    
    # Check if a refresh is forced
    force_refresh = kwargs.get("refresh_macro", False)
    
    if not force_refresh:
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(ResearchCache).where(
                    ResearchCache.key == cache_key,
                    ResearchCache.expire_at > datetime.now(timezone.utc).replace(tzinfo=None)
                )
                result = await db.execute(stmt)
                cached = result.scalar_one_or_none()
                if cached:
                    return cached.content
            except Exception as e:
                print(f"Cache check error in get_key_macro_indicators: {e}")

    # 2. Cache Miss - Fetch all data in parallel
    tasks = [
        fed_service.get_series_data("GDP", limit=4),
        fed_service.get_series_data("CPI", limit=6),
        fed_service.get_series_data("FEDFUNDS", limit=6),
        fed_service.get_series_data("PAYEMS", limit=6),
        fed_service.get_series_data("DXY", limit=6),
        calendar_service.get_upcoming_events(days=7)
    ]
    
    results = await asyncio.gather(*tasks)
    gdp_data, cpi_data, rates_data, payrolls_data, dxy_data, events = results
    
    output = ["### Key US Macroeconomic Indicators"]
    
    output.append("\n#### The Inflation Pulse & Currency")
    output.append(format_series("CPI (Consumer Price Index)", cpi_data, "Index"))
    output.append(format_series("US Dollar Index (DXY)", dxy_data, "Index"))
    
    output.append("\n#### Labor Market Dynamics")
    output.append(format_series("Non-Farm Payrolls", payrolls_data, "Thousands"))
    
    output.append("\n#### Yields & Monetary Policy")
    output.append(format_series("Effective Federal Funds Rate", rates_data, "%"))
    output.append(format_series("Real GDP Growth", gdp_data, "% (Quarterly)"))
    
    output.append("\n### Upcoming High-Impact US Events (Next 7 Days)")
    if not events:
        output.append("- No high-impact events scheduled.")
    else:
        for event in events:
            output.append(f"- **{event['time']}**: {event['event']} (Est: {event.get('estimate', 'N/A')}, Prev: {event.get('previous', 'N/A')})")
            
    final_report = "\n".join(output) + "\n"

    # 3. Save to Cache
    # Expire at the end of the day (23:59:59 UTC)
    tomorrow_midnight = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    expire_at = tomorrow_midnight.replace(tzinfo=None)

    async with AsyncSessionLocal() as db:
        try:
            new_cache = ResearchCache(
                source_type=ResearchSourceType.MACRO,
                key=cache_key,
                content=final_report,
                expire_at=expire_at
            )
            db.add(new_cache)
            await db.commit()
        except Exception as e:
            print(f"Cache save error in get_key_macro_indicators: {e}")

    return final_report
