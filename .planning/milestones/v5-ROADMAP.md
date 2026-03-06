# Roadmap - Milestone 5: Daily Proactive Analysis

This roadmap focuses on transforming the StockPlanner backend into a proactive financial assistant through scheduled tasks, deep research agents, and daily personalized reports.

## Phase 21: Deep News Aggregator
**Goal:** Implement a robust news fetching system beyond standard `yfinance` and `ddgs`.
- [ ] Integration with additional financial news sources.
- [ ] Improved article deduplication and clustering.
- [ ] Implementation of source-weighted sentiment analysis.

## Phase 22: Portfolio Performance & Benchmarking
**Goal:** Implementation of core daily performance metrics for users.
- [ ] Automated calculation of portfolio Alpha/Beta.
- [ ] Sector-wise performance attribution.
- [ ] Historical P/L tracking for proactive alerts.

## Phase 23: Daily Briefing Generator (MVP)
**Goal:** Create a unified engine for synthesizing daily reports.
- [ ] Generation of a multi-section PDF/Markdown report.
- [ ] Saving reports as "Briefings" in the database.
- [ ] Personalized section on macro impact on holdings.

## Phase 24: Scheduled Jobs & Delivery
**Goal:** Automate the entire process for all users.
- [ ] Integration with `APScheduler` for multi-timezone triggers.
- [ ] API endpoint for retrieving the latest briefing (`/reports/latest-briefing`).
- [ ] Resilience: Handling API rate limits during bulk generation.
