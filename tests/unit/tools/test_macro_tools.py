import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.tools.macro import get_key_macro_indicators, get_political_sentiment
from src.graph.tools.sentiment import SentimentResult
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_get_key_macro_indicators_cache_hit():
    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    cache_key = f"macro_{today_str}"
    
    mock_cached = MagicMock()
    mock_cached.content = "Cached Macro Report"
    
    with patch("src.graph.tools.macro.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cached
        mock_session.execute.return_value = mock_result
        
        result = await get_key_macro_indicators()
        assert result == "Cached Macro Report"

@pytest.mark.asyncio
async def test_get_key_macro_indicators_full_flow():
    """Test the full macro fetch logic including commodities, sectors, and LLM synthesis."""
    mock_fed_data = [{"date": "2024-02-01", "value": "3.1"}]
    mock_events = [{"time": "2024-03-05", "event": "FOMC", "estimate": "N/A", "previous": "N/A"}]
    mock_perf = {"Gold": "2000.00 (+1.00% over 5D)"}
    
    # Mock LLM response
    mock_llm_response = MagicMock()
    mock_llm_response.content = "LLM Market Analysis Summary"

    with patch("src.graph.tools.macro.AsyncSessionLocal") as mock_session_factory, \
         patch("src.graph.tools.macro.fed_service.get_series_data", new_callable=AsyncMock) as mock_fed, \
         patch("src.graph.tools.macro.calendar_service.get_upcoming_events", new_callable=AsyncMock) as mock_cal, \
         patch("src.graph.tools.macro.get_performance_summary", new_callable=AsyncMock) as mock_summary, \
         patch("langchain_openai.ChatOpenAI.ainvoke", new_callable=AsyncMock) as mock_llm:
        
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # 1. Cache Miss
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # 2. Service/Tool Mocks
        mock_fed.return_value = mock_fed_data
        mock_cal.return_value = mock_events
        mock_summary.return_value = mock_perf
        mock_llm.return_value = mock_llm_response
        
        result = await get_key_macro_indicators()
        
        # 3. Assertions
        assert "Key US Macroeconomic Indicators" in result
        assert "Commodity & Sector Trends" in result
        assert "LLM Market Analysis Summary" in result
        assert "FOMC" in result
        assert "3.1" in result
        
        # Verify save to cache was called
        assert mock_session.add.called
        assert mock_session.commit.called

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
        assert "0.80" in result
