import logging
from typing import List, Dict

import tweepy

from src.config import settings

logger = logging.getLogger(__name__)

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
        Returns a list of simplified tweet objects or empty list if no client/data.
        """
        if not self.client:
            logger.warning(f"X client not initialized. Cannot fetch tweets for {ticker}.")
            return []

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
            logger.error(f"Error fetching tweets for {ticker}: {e}")
            return []

    async def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch recent tweets for a specific username (e.g., realDonaldTrump).
        """
        if not self.client:
            logger.warning(f"X client not initialized. Cannot fetch tweets for user {username}.")
            return []

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
            logger.error(f"Error fetching tweets for {username}: {e}")
            return []

x_client = XClient()
