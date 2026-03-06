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
        assert "mock_1" in tweets[0]["id"]

@pytest.mark.asyncio
async def test_x_client_user_mock_fallback():
    with patch("src.config.settings.X_BEARER_TOKEN", None):
        client = XClient()
        tweets = await client.get_user_tweets("realDonaldTrump")
        assert len(tweets) > 0
        assert "mock_u1" in tweets[0]["id"]

@pytest.mark.asyncio
async def test_x_client_get_recent_cashtag_tweets_api_call():
    # Test successful API call
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.search_recent_tweets", new_callable=AsyncMock) as mock_search:
        
        mock_response = MagicMock()
        mock_tweet = MagicMock()
        mock_tweet.id = 12345
        mock_tweet.text = "Bullish on $AAPL"
        mock_tweet.created_at = "2026-03-04"
        mock_tweet.public_metrics = {"like_count": 10}
        
        mock_response.data = [mock_tweet]
        mock_search.return_value = mock_response
        
        client = XClient()
        tweets = await client.get_recent_cashtag_tweets("AAPL")
        
        assert len(tweets) == 1
        assert tweets[0]["id"] == "12345"
        assert "AAPL" in tweets[0]["text"]

@pytest.mark.asyncio
async def test_x_client_get_recent_cashtag_tweets_no_data():
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.search_recent_tweets", new_callable=AsyncMock) as mock_search:
        
        mock_response = MagicMock()
        mock_response.data = None
        mock_search.return_value = mock_response
        
        client = XClient()
        tweets = await client.get_recent_cashtag_tweets("AAPL")
        assert tweets == []

@pytest.mark.asyncio
async def test_x_client_get_recent_cashtag_tweets_exception():
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.search_recent_tweets", side_effect=Exception("API Error")):
        
        client = XClient()
        # Should fallback to mock on exception
        tweets = await client.get_recent_cashtag_tweets("AAPL")
        assert len(tweets) > 0
        assert "mock_1" in tweets[0]["id"]

@pytest.mark.asyncio
async def test_x_client_user_api_call_success():
    # Test successful user tweets API call
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.get_user", new_callable=AsyncMock) as mock_get_user, \
         patch("tweepy.asynchronous.AsyncClient.get_users_tweets", new_callable=AsyncMock) as mock_search:
        
        mock_user = MagicMock()
        mock_user.data.id = "123"
        mock_get_user.return_value = mock_user

        mock_response = MagicMock()
        mock_tweet = MagicMock()
        mock_tweet.id = 12345
        mock_tweet.text = "Test tweet content"
        mock_tweet.created_at = "2026-03-04"
        mock_tweet.public_metrics = {"like_count": 5}
        
        mock_response.data = [mock_tweet]
        mock_search.return_value = mock_response
        
        client = XClient()
        tweets = await client.get_user_tweets("realDonaldTrump")
        
        assert len(tweets) == 1
        assert tweets[0]["id"] == "12345"
        assert tweets[0]["text"] == "Test tweet content"

@pytest.mark.asyncio
async def test_x_client_user_api_call_no_user():
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.get_user", new_callable=AsyncMock) as mock_get_user:
        
        mock_get_user.return_value = None
        client = XClient()
        tweets = await client.get_user_tweets("nonexistent")
        assert tweets == []

@pytest.mark.asyncio
async def test_x_client_user_api_call_no_tweets():
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.get_user", new_callable=AsyncMock) as mock_get_user, \
         patch("tweepy.asynchronous.AsyncClient.get_users_tweets", new_callable=AsyncMock) as mock_search:
        
        mock_user = MagicMock()
        mock_user.data.id = "123"
        mock_get_user.return_value = mock_user
        
        mock_response = MagicMock()
        mock_response.data = None
        mock_search.return_value = mock_response
        
        client = XClient()
        tweets = await client.get_user_tweets("realDonaldTrump")
        assert tweets == []

@pytest.mark.asyncio
async def test_x_client_user_api_call_exception():
    with patch("src.config.settings.X_BEARER_TOKEN", "fake_token"), \
         patch("tweepy.asynchronous.AsyncClient.get_user", side_effect=Exception("API Error")):
        
        client = XClient()
        # Should fallback to mock on exception
        tweets = await client.get_user_tweets("realDonaldTrump")
        assert len(tweets) > 0
        assert "mock_u1" in tweets[0]["id"]
