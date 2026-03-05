import asyncio
from typing import List, Dict, Optional

import tweepy

from src.config import settings

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

    async def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch recent tweets for a specific username (e.g., realDonaldTrump).
        """
        if not self.client:
            return self._get_mock_user_tweets(username)

        try:
            user = await self.client.get_user(username=username)
            if not user or not user.data:
                return []
            
            user_id = user.data.id
            response = await self.client.get_users_tweets(
                id=user_id,
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
            print(f"Error fetching tweets for {username}: {e}")
            return self._get_mock_user_tweets(username)

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

    def _get_mock_user_tweets(self, username: str) -> List[Dict]:
        """
        Fallback mock data for user monitoring.
        """
        return [
            {
                "id": "mock_u1",
                "text": f"Markets are doing great! Best numbers ever. #MAGA",
                "created_at": "2026-03-04T09:00:00Z",
                "metrics": {"like_count": 50000, "retweet_count": 12000}
            },
            {
                "id": "mock_u2",
                "text": f"Tariffs are the greatest thing! We will bring back jobs. 🇺🇸",
                "created_at": "2026-03-04T10:30:00Z",
                "metrics": {"like_count": 45000, "retweet_count": 11000}
            }
        ]

x_client = XClient()
