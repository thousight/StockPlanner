import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from langchain_openai import ChatOpenAI
from sqlalchemy import select

from src.database.session import AsyncSessionLocal
from src.database.models import ResearchCache, ResearchSourceType
from src.services.macro import fed_service, calendar_service
from src.services.market_data import get_historical_prices_async
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

COMMODITIES = {
    "Gold": "GLD",
    "Crude Oil": "USO",
    "Natural Gas": "UNG",
    "Copper": "CPER",
    "Silver": "SLV"
}

SECTORS = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Communication Services": "XLC"
}

async def get_performance_summary(symbols_map: Dict[str, str]) -> Dict[str, str]:
    """Helper to fetch 5-day performance for a map of names to symbols."""
    tasks = [get_historical_prices_async(sym, period="5d") for sym in symbols_map.values()]
    histories = await asyncio.gather(*tasks)
    
    performance = {}
    for (name, sym), hist in zip(symbols_map.items(), histories):
        if not hist.empty and len(hist) > 1:
            latest = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[0]
            change = ((latest - prev) / prev) * 100
            performance[name] = f"{latest:.2f} ({change:+.2f}% over 5D)"
        else:
            performance[name] = "Data unavailable"
    return performance

async def get_key_macro_indicators(**kwargs) -> str:
    """
    Fetch the latest key US macroeconomic indicators (GDP, CPI, Payrolls, Interest Rates, DXY),
    upcoming high-impact events, and trends in key commodities and market sectors.
    """
    # 1. Check Cache
    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    cache_key = f"macro_{today_str}"
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

    # 2. Fetch All Data
    tasks = [
        fed_service.get_series_data("GDP", limit=4),
        fed_service.get_series_data("CPI", limit=6),
        fed_service.get_series_data("FEDFUNDS", limit=6),
        fed_service.get_series_data("PAYEMS", limit=6),
        fed_service.get_series_data("DXY", limit=6),
        calendar_service.get_upcoming_events(days=7),
        get_performance_summary(COMMODITIES),
        get_performance_summary(SECTORS)
    ]
    
    results = await asyncio.gather(*tasks)
    gdp_data, cpi_data, rates_data, payrolls_data, dxy_data, events, commodity_perf, sector_perf = results
    
    # 3. Build Raw Data String for LLM Analysis
    raw_data = [
        "### Macro Data",
        format_series("CPI", cpi_data, "Index"),
        format_series("DXY", dxy_data, "Index"),
        format_series("Payrolls", payrolls_data, "Thousands"),
        format_series("Fed Funds", rates_data, "%"),
        format_series("GDP", gdp_data, "%"),
        "\n### Commodities (5D)",
        "\n".join([f"- {k}: {v}" for k, v in commodity_perf.items()]),
        "\n### Sectors (5D)",
        "\n".join([f"- {k}: {v}" for k, v in sector_perf.items()])
    ]
    
    # 4. Synthesize Analysis with LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    analysis_prompt = f"""
    Analyze the following market data and provide:
    1. A summary of commodity trends and their likely impact on the economy (e.g. inflation, manufacturing).
    2. A summary of sector performance and what it signals about market leadership or risk appetite.
    3. How these trends correlate with the macro indicators provided.

    Data:
    {chr(10).join(raw_data)}
    """
    
    analysis_response = await llm.ainvoke(analysis_prompt)
    analysis_text = analysis_response.content

    # 5. Format Final Output
    output = ["### Key US Macroeconomic Indicators"]
    output.append("\n#### The Inflation Pulse & Currency")
    output.append(format_series("CPI (Consumer Price Index)", cpi_data, "Index"))
    output.append(format_series("US Dollar Index (DXY)", dxy_data, "Index"))
    
    output.append("\n#### Labor Market Dynamics")
    output.append(format_series("Non-Farm Payrolls", payrolls_data, "Thousands"))
    
    output.append("\n#### Yields & Monetary Policy")
    output.append(format_series("Effective Federal Funds Rate", rates_data, "%"))
    output.append(format_series("Real GDP Growth", gdp_data, "% (Quarterly)"))
    
    output.append("\n### Commodity & Sector Trends")
    output.append(analysis_text)
    
    output.append("\n### Upcoming High-Impact US Events (Next 7 Days)")
    if not events:
        output.append("- No high-impact events scheduled.")
    else:
        for event in events:
            output.append(f"- **{event['time']}**: {event['event']} (Est: {event.get('estimate', 'N/A')}, Prev: {event.get('previous', 'N/A')})")
            
    final_report = "\n".join(output) + "\n"

    # 6. Save to Cache
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
