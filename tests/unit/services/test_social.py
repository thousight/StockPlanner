import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.social import XClient

@pytest.mark.asyncio
async def test_x_client_mock_fallback():
    # Test that it falls back to mock if no client initialized
    with patch("src.config.settings.X_BEARER_TOKEN", None):
        client = XClient()
        tweets = await client.get_recent_cashtag_tweets("AAPL")
        assert len(tweets) > 0
        assert "mock_" in tweets[0]["id"]

@pytest.mark.asyncio
async def test_x_client_api_call():
    # Test that it calls the real API if client initialized
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.search_recent_tweets", new_callable=AsyncMock) as mock_search:
        
        mock_response = MagicMock()
        mock_tweet = MagicMock()
        mock_tweet.id = 12345
        mock_tweet.text = "Test tweet content"
        mock_tweet.created_at = "2026-03-04"
        mock_tweet.public_metrics = {"like_count": 5}
        
        mock_response.data = [mock_tweet]
        mock_search.return_value = mock_response
        
        client = XClient()
        tweets = await client.get_recent_cashtag_tweets("AAPL")
        
        assert len(tweets) == 1
        assert tweets[0]["id"] == "12345"
        assert tweets[0]["text"] == "Test tweet content"
