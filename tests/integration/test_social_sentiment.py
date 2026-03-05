import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.tools.sentiment import analyze_sentiment, get_market_sentiment, SentimentResult

@pytest.mark.asyncio
async def test_analyze_sentiment_positive():
    text = "NVIDIA reports record-breaking Q4 revenue, exceeding analyst expectations and raising 2026 guidance."
    # We use real LLM here if OPENAI_API_KEY is available, or we could mock it.
    # For integration test, let's mock it to avoid token costs and ensure deterministic results.
    mock_res = SentimentResult(sentiment_score=0.9, rationale="Strong revenue beat and raised guidance.")
    
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_structured:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_res
        mock_structured.return_value = mock_chain
        
        result = await analyze_sentiment(text)
        assert result.sentiment_score > 0.5
        assert "revenue" in result.rationale.lower()

@pytest.mark.asyncio
async def test_get_market_sentiment_aggregation(mocker):
    ticker = "NVDA"
    
    # Mock all internal tool calls
    mocker.patch("src.graph.tools.sentiment.get_stock_news", return_value="Positive news summary.")
    mocker.patch("src.graph.tools.sentiment.get_sec_filing_section", return_value="Item 1A risk factors.")
    mocker.patch("src.services.social.x_client.get_recent_cashtag_tweets", return_value=[{"text": "Bullish on $NVDA!"}])
    mocker.patch("src.graph.tools.sentiment.fetch_ddgs_urls", return_value=[{"title": "Reddit post about NVDA"}])
    
    # Mock analyze_sentiment for each call
    mock_sentiments = [
        SentimentResult(sentiment_score=0.7, rationale="News is positive."),
        SentimentResult(sentiment_score=0.2, rationale="SEC risks are standard."),
        SentimentResult(sentiment_score=0.9, rationale="Social is very bullish."),
        SentimentResult(sentiment_score=0.8, rationale="Reddit is hyped.")
    ]
    
    with patch("src.graph.tools.sentiment.analyze_sentiment", side_effect=mock_sentiments):
        result = await get_market_sentiment(ticker)
        assert f"Market Sentiment for {ticker}" in result
        assert "Aggregate Score:" in result
        # Check if breakdown is present
        assert "News" in result
        assert "SEC" in result
        assert "X (Social)" in result
        assert "Reddit (Social)" in result

@pytest.mark.asyncio
async def test_x_client_mock():
    from src.services.social import x_client
    # Should use fallback mock
    tweets = await x_client.get_recent_cashtag_tweets("AAPL")
    assert len(tweets) > 0
    assert "mock_" in tweets[0]["id"]
