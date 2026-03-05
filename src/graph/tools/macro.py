import asyncio
from datetime import datetime
from typing import Dict, List

from src.services.macro import fed_service, calendar_service
from src.graph.tools.sentiment import analyze_sentiment
from src.database.models import ResearchSourceType
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
        key=f"political_{username}_{datetime.now().strftime('%Y%m%d%H')}"
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
    """
    # Fetch all series in parallel
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
            
    return "\n".join(output) + "\n"
