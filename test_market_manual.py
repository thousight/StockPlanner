from src.tools.market import get_current_price, get_stock_news, get_company_info

print("Testing Market Tools...")

symbol = "AAPL"

price = get_current_price(symbol)
print(f"Price of {symbol}: {price}")

info = get_company_info(symbol)
print(f"Info for {symbol}: {info}")

news = get_stock_news(symbol, max_results=2)
print(f"News for {symbol}: {len(news)} items found.")
if news:
    print(f"First news item: {news[0]['title']}")
