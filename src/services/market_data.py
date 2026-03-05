import asyncio
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import FXRate, Asset, AssetType, Transaction, RecordStatus
import yfinance as yf

def get_ticker(symbol: str) -> yf.Ticker:
    """
    Returns a yfinance Ticker object.
    """
    return yf.Ticker(symbol)

async def get_historical_fx_rate(db: AsyncSession, source: str, target: str = "USD", transaction_date: date = None) -> Decimal:
    """
    Fetch historical FX rate. Returns target/source rate (e.g., EURUSD=X rate if source=EUR, target=USD).
    Uses caching in fx_rates table and fallback to nearest available date.
    """
    if source == target:
        return Decimal("1.0")
    
    if transaction_date is None:
        transaction_date = date.today()

    # 1. Check cache
    stmt = (
        select(FXRate)
        .where(FXRate.source == source, FXRate.target == target, FXRate.date <= transaction_date)
        .order_by(FXRate.date.desc())
        .limit(1)
    )
    result_proxy = await db.execute(stmt)
    result = result_proxy.scalar_one_or_none()
    
    if result and result.date == transaction_date:
        return result.rate
    
    # 2. If not in cache or not exact date, try to fetch from yfinance
    ticker_symbol = f"{source}{target}=X"
    try:
        ticker = get_ticker(ticker_symbol)
        # Fetch data for a range around the date
        start_str = transaction_date.strftime('%Y-%m-%d')
        end_str = (transaction_date + timedelta(days=1)).strftime('%Y-%m-%d')
        
        hist = await asyncio.to_thread(ticker.history, start=start_str, end=end_str)
        
        if hist.empty:
            hist = await asyncio.to_thread(ticker.history, period="5d")
        
        if not hist.empty:
            rate = Decimal(str(hist['Close'].iloc[-1]))
            
            # Cache it
            new_rate = FXRate(source=source, target=target, rate=rate, date=transaction_date)
            db.add(new_rate)
            await db.commit()
            return rate
    except Exception as e:
        print(f"Error fetching FX rate for {ticker_symbol}: {e}")
    
    # 3. Fallback to nearest in cache if yfinance fails
    if result:
        return result.rate
        
    return Decimal("1.0")

async def validate_transaction_price(symbol: str, transaction_date: date, price: Decimal) -> bool:
    """
    Validates if the entered price is within a reasonable range (+/- 10%) of the 
    historical high/low for that day using yfinance.
    """
    try:
        ticker = get_ticker(symbol)
        start_date = transaction_date
        end_date = transaction_date + timedelta(days=1)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        hist = await asyncio.to_thread(ticker.history, start=start_str, end=end_str)
        
        if hist.empty:
            return True
            
        day_low = Decimal(str(hist['Low'].iloc[0]))
        day_high = Decimal(str(hist['High'].iloc[0]))
        
        buffer = Decimal("0.10")
        min_allowed = day_low * (Decimal("1.0") - buffer)
        max_allowed = day_high * (Decimal("1.0") + buffer)
        
        return min_allowed <= price <= max_allowed
    except Exception as e:
        print(f"Error validating price for {symbol}: {e}")
        return True

async def get_current_price(db: AsyncSession, asset: Asset) -> Decimal:
    """
    Fetch the latest market price for an asset.
    """
    if asset.type == AssetType.STOCK:
        ticker = get_ticker(asset.symbol)
        try:
            # fast_info is a property that might trigger network calls
            fast_info = await asyncio.to_thread(lambda: ticker.fast_info)
            price = Decimal(str(fast_info['last_price']))
            if price > 0:
                return price
        except Exception as e:
            print(f"Error fetching current price for {asset.symbol}: {e}")
            try:
                hist = await asyncio.to_thread(ticker.history, period="1d")
                if not hist.empty:
                    return Decimal(str(hist['Close'].iloc[-1]))
            except Exception:
                pass

    # Fallback for all assets
    stmt = (
        select(Transaction.price_base)
        .where(Transaction.asset_id == asset.id, Transaction.status == RecordStatus.ACTIVE)
        .order_by(Transaction.date.desc())
        .limit(1)
    )
    result_proxy = await db.execute(stmt)
    last_price = result_proxy.scalar_one_or_none()
    
    if last_price:
        return Decimal(str(last_price))
    
    return Decimal("0")

async def get_historical_prices_async(symbol: str, period: str = "1mo", interval: str = "1d", start=None, end=None):
    """
    Fetch historical prices for a symbol.
    """
    ticker = get_ticker(symbol)
    if start and end:
        return await asyncio.to_thread(ticker.history, start=start, end=end, interval=interval)
    return await asyncio.to_thread(ticker.history, period=period, interval=interval)

async def get_stock_financials_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch fundamental financial data for a specific ticker.
    """
    ticker = get_ticker(symbol)
    return await asyncio.to_thread(lambda: ticker.info)

async def get_stock_news_data(symbol: str) -> List[Dict[str, Any]]:
    """
    Fetch news for a specific ticker.
    """
    ticker = get_ticker(symbol)
    return await asyncio.to_thread(lambda: ticker.news)

def _parse_yf_news_item(item: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Parse a yfinance news item."""
    try:
        if 'content' in item:
            content = item['content']
            title = content.get('title')
            link = None
            if 'clickThroughUrl' in content and content['clickThroughUrl']:
                link = content['clickThroughUrl'].get('url')
            if not link and 'canonicalUrl' in content and content['canonicalUrl']:
                link = content['canonicalUrl'].get('url')
            if title and link:
                return {"title": title, "link": link}
        elif 'title' in item and 'link' in item:
            return {
                "title": item.get('title'),
                "link": item.get('link'),
            }
    except Exception as e:
        print(f"Error parsing news item: {e}")
    return None

async def fetch_yfinance_news_urls(ticker_symbol: str) -> List[Dict[str, str]]:
    """Fetch news URLs for a single ticker."""
    results = []
    try:
        news_items = await get_stock_news_data(ticker_symbol)
        if news_items:
            for item in news_items:
                parsed = _parse_yf_news_item(item)
                if parsed:
                    results.append(parsed)
    except Exception as e:
        print(f"Error fetching news for {ticker_symbol}: {e}")
    return results
