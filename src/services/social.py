import tweepy
from src.config import settings
from typing import List, Dict, Optional
import asyncio

class XClient:
    """
    Client for X (Twitter) API v2 using Tweepy async support.
    """
    def __init__(self):
        self.bearer_token = settings.X_BEARER_TOKEN
        self.client = None
        if self.bearer_token:
            self.client = tweepy.asynchronous.AsyncClient(
                bearer_token=self.bearer_token,
                consumer_key=settings.X_API_KEY,
                consumer_secret=settings.X_API_SECRET,
                access_token=settings.X_ACCESS_TOKEN,
                access_token_secret=settings.X_ACCESS_TOKEN_SECRET
            )

    async def get_recent_cashtag_tweets(self, ticker: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch recent tweets for a specific cashtag (e.g., $AAPL).
        Returns a list of simplified tweet objects.
        """
        if not self.client:
            return self._get_mock_tweets(ticker)

        try:
            query = f"${ticker} -is:retweet lang:en"
            response = await self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'text']
            )
            
            if not response or not response.data:
                return []

            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": str(tweet.id),
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "metrics": tweet.public_metrics
                })
            return tweets
        except Exception as e:
            print(f"Error fetching tweets for {ticker}: {e}")
            return self._get_mock_tweets(ticker)

    def _get_mock_tweets(self, ticker: str) -> List[Dict]:
        """
        Fallback mock data for development.
        """
        return [
            {
                "id": "mock_1",
                "text": f"Just bought more ${ticker}! Look at that growth. 🚀",
                "created_at": "2026-03-04T10:00:00Z",
                "metrics": {"like_count": 10, "retweet_count": 2}
            },
            {
                "id": "mock_2",
                "text": f"I'm worried about ${ticker}'s latest margins. Might be time to sell. #stocks",
                "created_at": "2026-03-04T11:30:00Z",
                "metrics": {"like_count": 5, "retweet_count": 1}
            }
        ]

x_client = XClient()
