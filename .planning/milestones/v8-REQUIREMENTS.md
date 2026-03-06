# Requirements - Milestone 8: Daily Proactive Analysis

This milestone shifts the system from a reactive chat-based interface to a proactive financial coach that provides daily insights, portfolio monitoring, and deep research summaries.

## 1. Deep Research & News Aggregation

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-800** | **Comprehensive News Scraping**: Implementation of a robust news aggregator that fetches from multiple financial sources (Reuters, Bloomberg, CNBC, Financial Times) via structured search and direct scraping. | P0 | [ ] |
| **REQ-801** | **Article Clustering**: Grouping related news articles by topic or ticker to prevent duplicate summaries and identify emerging narratives. | P1 | [ ] |
| **REQ-802** | **Sentiment Scoring**: Automated sentiment analysis for each news cluster, weighted by source authority and recency. | P1 | [ ] |

## 2. Proactive Portfolio Analysis

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-810** | **Daily Performance Engine**: Background job to calculate daily performance metrics (P/L, Alpha, Beta) for all user portfolios relative to benchmarks (SPY, QQQ). | P0 | [ ] |
| **REQ-811** | **Portfolio Health Check**: Identifying risks such as over-concentration, high correlation with macro factors, or significant recent volatility in specific holdings. | P1 | [ ] |
| **REQ-812** | **Personalized Daily Briefing**: Generation of a multi-section summary covering: 1. Portfolio Performance, 2. Top News Impacting Holdings, 3. Relevant Macro Shifts. | P0 | [ ] |

## 3. Automation & Delivery

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-820** | **Scheduled Reporting**: Integration with APScheduler to trigger daily briefings at market close or pre-market open for each user's timezone. | P0 | [ ] |
| **REQ-821** | **Briefing Storage**: Saving generated briefings as a special category of `Report` in PostgreSQL for historical review. | P0 | [ ] |
| **REQ-822** | **Notification Readiness**: Endpoint for mobile clients to check for the latest daily briefing or receive "push" triggers (webhook/callback ready). | P1 | [ ] |
