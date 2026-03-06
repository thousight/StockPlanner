# Phase 21 Context: Deep News Aggregator

## Overview
The current news fetching mechanism relies primarily on `yfinance` for ticker-specific news and DuckDuckGo for general web search. While functional, it is reactive and lacks depth. Phase 21 aims to build a proactive news aggregator that can:
1. Scan multiple high-authority financial domains.
2. Group related stories (clustering) to avoid redundant synthesis.
3. Provide a structured "Narrative Delta" (how has the story changed in the last 24 hours?).

## Current Infrastructure
- `src/graph/utils/news.py`: Handles individual article scraping and LLM-based summarization.
- `src/graph/utils/scraping.py`: Clean HTML content extraction.
- `ResearchCache`: Used to prevent re-scraping the same URL within 7 days.

## Strategic Direction
- **Source Expansion**: Use RSS feeds or well-known URL patterns for top sources (Reuters, CNBC, Bloomberg - where possible).
- **Clustering**: Use an LLM to compare article headlines and summaries to identify the same underlying story.
- **DeepResearch Node**: A specialized LangGraph node that is only triggered when a user (or the system in proactive mode) requests a deep dive.

## Key Constraints
- **Scraping Policies**: Must respect robots.txt and use reasonable User-Agents.
- **Latency**: Deep research can be slow; async parallel fetching is essential.
- **Token Usage**: Must prioritize high-signal content to avoid bloating the LLM context.
