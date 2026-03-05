import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.tools.macro import get_key_macro_indicators, get_political_sentiment
from src.graph.tools.sentiment import SentimentResult

@pytest.mark.asyncio
async def test_get_key_macro_indicators_success():
    mock_fed_data = [{"date": "2024-01-01", "value": "2.5"}]
    mock_events = [{"time": "2024-03-04", "event": "FOMC", "estimate": "5.5", "previous": "5.5"}]
    
    with patch("src.graph.tools.macro.fed_service.get_series_data", new_callable=AsyncMock) as mock_fed, \
         patch("src.graph.tools.macro.calendar_service.get_upcoming_events", new_callable=AsyncMock) as mock_cal:
        
        mock_fed.return_value = mock_fed_data
        mock_cal.return_value = mock_events
        
        result = await get_key_macro_indicators()
        assert "Key US Macroeconomic Indicators" in result
        assert "CPI" in result
        assert "FOMC" in result
        assert "2.5" in result

@pytest.mark.asyncio
async def test_get_political_sentiment_success():
    mock_tweets = [
        {"text": "Big trade deal!", "metrics": {"like_count": 1000}}
    ]
    mock_sentiment = SentimentResult(sentiment_score=0.8, rationale="Positive trade talk.")
    
    with patch("src.graph.tools.macro.x_client.get_user_tweets", new_callable=AsyncMock) as mock_x, \
         patch("src.graph.tools.macro.analyze_sentiment", new_callable=AsyncMock) as mock_analyze:
        
        mock_x.return_value = mock_tweets
        mock_analyze.return_value = mock_sentiment
        
        result = await get_political_sentiment()
        assert "Political Sentiment Monitoring" in result
        assert "@realDonaldTrump" in result
        assert "0.80" in result
        assert "Big trade deal!" in result

@pytest.mark.asyncio
async def test_get_political_sentiment_no_data():
    with patch("src.graph.tools.macro.x_client.get_user_tweets", new_callable=AsyncMock) as mock_x:
        mock_x.return_value = []
        result = await get_political_sentiment()
        assert "No recent updates found" in result
