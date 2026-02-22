import yfinance as yf
from typing import List
from concurrent.futures import ThreadPoolExecutor
from src.utils.news import get_summary_result, fetch_yfinance_news_urls, fetch_ddgs_urls, _parse_yf_news_item

def get_stock_news(symbol: str, max_results: int = 3) -> str:
    """
    Fetch and summarize the latest news for a specific stock ticker.
    """
    results = []
    try:
        stock = yf.Ticker(symbol)
        news_items = stock.news
        
        if not news_items:
             return None

        for item in news_items[:max_results]:
            parsed = _parse_yf_news_item(item)
            if not parsed:
                continue
                
            result = get_summary_result(parsed)
            if result:
                results.append(result)
                
        if not results:
             return None
             
        result_lines = [f"News for {symbol}:"]
        for item in results:
            result_lines.append(f"- **{item['title']}**: {item['summary']} (URL: {item['url']})")
            
        return "\n".join(result_lines) + "\n"
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return f"Error fetching news for {symbol}: {e}\n"

def get_macro_economic_news() -> str:
    """
    Fetch and summarize the latest global macroeconomic news and indicators.
    """
    title_and_urls = []

    # 1. Collect URLs from yfinance tickers in parallel
    tickers = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB"]
    with ThreadPoolExecutor(max_workers=4) as executor:
        for result in executor.map(fetch_yfinance_news_urls, tickers):
            title_and_urls.extend(result)
    
    # 2. Collect URLs from DuckDuckGo queries in parallel
    queries = [
        "Macroeconomics news today",
        "US economy outlook today",
        "Federal Reserve interest rates news",
        "US employment report news",
        "US inflation cpi report news",
    ]
    with ThreadPoolExecutor(max_workers=5) as executor:
        for result in executor.map(fetch_ddgs_urls, queries):
            title_and_urls.extend(result)
            
    # 3. Deduplicate by URL
    seen_urls = set()
    unique_candidates = []
    for item in title_and_urls:
        if item["link"] not in seen_urls:
            unique_candidates.append(item)
            seen_urls.add(item["link"])
            
    # 4. Fetch summaries in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_results = list(executor.map(get_summary_result, unique_candidates))
        
    valid_results = [r for r in all_results if r]
    if not valid_results:
         return None
         
    result_lines = ["Macro Economic News:"]
    for item in valid_results:
        result_lines.append(f"- **{item['title']}**: {item['summary']} (URL: {item['url']})")
        
    return "\n".join(result_lines) + "\n"

def web_search(queries: List[str]) -> str:
    """
    Perform web search and get title and page summary by the queries.
    Returns a formatted markdown string of the results grouped by query.
    """
    # 1. Fetch URLs for each query in parallel
    # list(executor.map) returns results in the exact same order as the input queries
    with ThreadPoolExecutor(max_workers=5) as executor:
        query_results = list(executor.map(fetch_ddgs_urls, queries))
    
    # 2. Collect unique candidate URLs to speed up summary extraction
    unique_candidates = {}
    for items in query_results:
        for item in items:
            link = item.get("link")
            if link and link not in unique_candidates:
                unique_candidates[link] = item
                
    # 3. Fetch summaries in parallel for unique candidates
    candidate_list = list(unique_candidates.values())
    with ThreadPoolExecutor(max_workers=5) as executor:
        summarized_results = list(executor.map(get_summary_result, candidate_list))
        
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
                result_lines.append(f"- **{summary_data['title']}**: {summary_data['summary']} (URL: {summary_data['url']})")
                seen_in_group.add(link)
                found_any = True
                
        if not found_any:
            result_lines.append("- No results found.")
            
    return "\n".join(result_lines) + "\n"
