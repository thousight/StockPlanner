# Phase 16 Research: Social & Sentiment

## 1. X/Twitter API Integration
- **Library Selection:** **Tweepy** with the `[async]` extra is the recommended choice. It provides a native `AsyncClient` for X API v2.
- **Async Engine:** Tweepy uses `aiohttp` for its async operations, which is compatible with our FastAPI/asyncio stack.
- **Endpoints of Interest:** 
  - `search_recent_tweets`: For fetching the latest "cashtags" (e.g., $AAPL).
  - `get_tweet`: For detailed metrics (likes, retweets) to help weigh sentiment.
- **Strategy:** Use `AsyncClient` with `Bearer Token` for read-only access to recent market sentiment.

## 2. Sentiment Engine (Numerical -1.0 to 1.0)
- **Model:** `gpt-4o` or `gpt-4o-mini` with `temperature: 0` for consistency.
- **Scoring Schema:**
  - `1.0`: Extreme Bullish (Major beat, transformative innovation).
  - `0.5`: Positive (Growth, dividend increase).
  - `0.0`: Neutral (Factual report, routine filing).
  - `-0.5`: Negative (Guidance cut, minor miss).
  - `-1.0`: Extreme Bearish (Bankruptcy risk, fraud).
- **Rationale:** The prompt must enforce a `rationale` field in the JSON output to explain the score (Chain-of-Thought).

## 3. Unified Scraping Strategy (`scraping.py`)
- **Pipeline:** "Clean then Extract".
- **Tools:**
  - `readability-lxml`: Used as a pre-processor to remove boilerplate/noise.
  - `BeautifulSoup (lxml parser)`: Used as a surgical extractor for specific sections or tables.
- **SEC Specifics:** While readability is great for text, we must ensure it doesn't strip tables. Using `doc.summary()` preserves the core HTML for BeautifulSoup.
- **User-Agent:** Standardize on the SEC-compliant string `StockPlanner/1.0 (contact@...)` to be safe across all platforms.

## 4. Social Media Scouting (Reddit/StockTwits)
- **Tool:** DuckDuckGo (`ddgs`) with site-specific operators.
- **Queries:**
  - `site:reddit.com/r/wallstreetbets "$TICKER"`
  - `site:stocktwits.com "$TICKER"`
- **Filtering:** Use the "Past 24 Hours" filter to ensure freshness.

## 5. Unified Database Cache (`ResearchCache`)
- **Schema Idea:**
  ```python
  class ResearchCache(Base):
      id = Column(Integer, primary_key=True)
      source_type = Column(String) # SEC, NEWS, SOCIAL, X
      ticker = Column(String)
      key = Column(String, unique=True) # URL or Tweet ID
      content = Column(Text)
      sentiment_score = Column(Float)
      sentiment_reason = Column(Text)
      expire_at = Column(DateTime)
      created_at = Column(DateTime)
  ```
- **TTL:** 24 hours for Social, 7 days for News/SEC.
