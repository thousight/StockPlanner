import asyncio
from typing import List
from src.graph.utils.news import get_summary_result, fetch_ddgs_urls
from src.services.market_data import fetch_yfinance_news_urls, _parse_yf_news_item, get_stock_news_data

async def get_stock_news(symbol: str, max_results: int = 3, **kwargs) -> str:
    """
    Fetch and summarize the latest news for a specific stock ticker.
    """
    results = []
    try:
        news_items = await get_stock_news_data(symbol)
        
        if not news_items:
             return None

        tasks = []
        for item in news_items[:max_results]:
            parsed = _parse_yf_news_item(item)
            if not parsed:
                continue
                
            parsed["user_agent"] = kwargs.get("user_agent", "")
            expire_at = kwargs.get("expire_at", None)
            tasks.append(get_summary_result(parsed, expire_at=expire_at))
            
        all_results = await asyncio.gather(*tasks)
        results = [r for r in all_results if r]
                
        if not results:
             return None
             
        result_lines = [f"News for {symbol}:"]
        for item in results:
            result_lines.append(f"- **{item['title']}**: {item['summary']}")
            
        return "\n".join(result_lines) + "\n"
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return f"Error fetching news for {symbol}: {e}\n"

async def get_macro_economic_news(**kwargs) -> str:
    """
    Fetch and summarize the latest global macroeconomic news and indicators.
    """
    title_and_urls = []

    # 1. Collect URLs from yfinance tickers
    tickers = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB"]
    for ticker in tickers:
        title_and_urls.extend(await fetch_yfinance_news_urls(ticker))
    
    # 2. Collect URLs from DuckDuckGo queries (Focused on narrative/geopolitical context)
    queries = [
        "Major global economic shifts news today",
        "Geopolitical tensions market impact",
        "Trade policy and tariff news",
        "US fiscal policy news",
    ]
    for query in queries:
        title_and_urls.extend(fetch_ddgs_urls(query))
            
    # 3. Deduplicate by URL
    seen_urls = set()
    unique_candidates = []
    for item in title_and_urls:
        if item["link"] not in seen_urls:
            item["user_agent"] = kwargs.get("user_agent", "")
            unique_candidates.append(item)
            seen_urls.add(item["link"])
            
    # 4. Fetch summaries in parallel
    expire_at = kwargs.get("expire_at", None)
    tasks = [get_summary_result(item, expire_at=expire_at) for item in unique_candidates]
    all_results = await asyncio.gather(*tasks)
        
    valid_results = [r for r in all_results if r]
    if not valid_results:
         return None
         
    result_lines = ["Macro Economic News:"]
    for item in valid_results:
        result_lines.append(f"- **{item['title']}**: {item['summary']}")
        
    return "\n".join(result_lines) + "\n"

async def web_search(queries: List[str], **kwargs) -> str:
    """
    Perform web search and get title and page summary by the queries.
    Returns a formatted markdown string of the results grouped by query.
    """
    # 1. Fetch URLs for each query
    # fetch_ddgs_urls is synchronous but we wrap it in basic loop for now
    query_results = [fetch_ddgs_urls(q) for q in queries]
    
    # 2. Collect unique candidate URLs to speed up summary extraction
    unique_candidates = {}
    for items in query_results:
        for item in items:
            link = item.get("link")
            if link and link not in unique_candidates:
                item["user_agent"] = kwargs.get("user_agent", "")
                unique_candidates[link] = item
                
    # 3. Fetch summaries in parallel for unique candidates
    candidate_list = list(unique_candidates.values())
    expire_at = kwargs.get("expire_at", None)
    tasks = [get_summary_result(item, expire_at=expire_at) for item in candidate_list]
    summarized_results = await asyncio.gather(*tasks)
        
    # Create a lookup mapping from URL to the summarized result
    summary_map = {}
    for res in summarized_results:
        if res and "url" in res:
            summary_map[res["url"]] = res
            
    # 4. Rebuild the final results grouped by query
    result_lines = ["Web Search Results:"]
    for i, items in enumerate(query_results):
        query = queries[i]
        result_lines.append(f"\nQuery: '{query}'")
        seen_in_group = set()
        found_any = False
        for item in items:
            link = item.get("link")
            # Ensure we have a valid summary and prevent exact duplicates per query
            if link and link in summary_map and link not in seen_in_group:
                summary_data = summary_map[link]
                result_lines.append(f"- **{summary_data['title']}**: {summary_data['summary']}")
                seen_in_group.add(link)
                found_any = True
                
        if not found_any:
            result_lines.append("- No results found.")
            
    return "\n".join(result_lines) + "\n"
