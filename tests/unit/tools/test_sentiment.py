import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.tools.sentiment import analyze_sentiment, get_market_sentiment, SentimentResult
from src.database.models import ResearchSourceType

@pytest.mark.asyncio
async def test_analyze_sentiment_caching(mocker):
    text = "Some financial text to analyze."
    key = "test_key"
    
    # 1. Test cache hit
    mock_cached = MagicMock()
    mock_cached.sentiment_score = 0.5
    mock_cached.sentiment_reason = "Cached reason"
    
    # Use a real-ish session mock or patch the database check
    with patch("src.graph.tools.sentiment.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cached
        mock_session.execute.return_value = mock_result
        
        result = await analyze_sentiment(text, key=key)
        assert result.sentiment_score == 0.5
        assert result.rationale == "Cached reason"

@pytest.mark.asyncio
async def test_analyze_sentiment_llm_call(mocker):
    text = "Some financial text to analyze."
    key = "new_key"
    
    with patch("src.graph.tools.sentiment.AsyncSessionLocal") as mock_session_factory, \
         patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_structured:
        
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # Mock cache miss
        mock_db_result = MagicMock()
        mock_db_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_db_result
        
        # Mock LLM
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = SentimentResult(sentiment_score=0.8, rationale="LLM reason")
        mock_structured.return_value = mock_chain
        
        result = await analyze_sentiment(text, key=key)
        assert result.sentiment_score == 0.8
        assert result.rationale == "LLM reason"
        assert mock_session.add.called

@pytest.mark.asyncio
async def test_get_market_sentiment_no_data(mocker):
    mocker.patch("src.graph.tools.sentiment.get_stock_news", return_value=None)
    mocker.patch("src.graph.tools.sentiment.get_sec_filing_section", return_value=None)
    mocker.patch("src.services.social.x_client.get_recent_cashtag_tweets", return_value=[])
    mocker.patch("src.graph.tools.sentiment.fetch_ddgs_urls", return_value=[])
    
    result = await get_market_sentiment("AAPL")
    assert "No data available" in result
