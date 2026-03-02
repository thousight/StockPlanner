from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.database.models import FXRate, Asset, AssetType
import yfinance as yf

def get_historical_fx_rate(db: Session, source: str, target: str = "USD", transaction_date: date = None) -> Decimal:
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
    result = db.execute(stmt).scalar_one_or_none()
    
    if result and result.date == transaction_date:
        return result.rate
    
    # 2. If not in cache or not exact date, try to fetch from yfinance
    # yfinance ticker format: EURUSD=X
    ticker_symbol = f"{source}{target}=X"
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetch data for a range around the date to handle weekends/holidays
        start_date = transaction_date
        # We might need to look back a few days
        hist = ticker.history(start=transaction_date.strftime('%Y-%m-%d'), end=(transaction_date.replace(day=transaction_date.day+1)).strftime('%Y-%m-%d'))
        
        if hist.empty:
            # Try to get the latest available price if it's a very recent date or weekend
            hist = ticker.history(period="5d")
        
        if not hist.empty:
            # Get the rate closest to the requested date
            # For simplicity, we'll take the 'Close' of the closest available date <= transaction_date
            # or just the last available if none <= transaction_date
            rate = Decimal(str(hist['Close'].iloc[-1]))
            
            # Cache it (even if it's not the exact date, it's the best we have)
            new_rate = FXRate(source=source, target=target, rate=rate, date=transaction_date)
            db.add(new_rate)
            db.commit()
            return rate
    except Exception as e:
        print(f"Error fetching FX rate for {ticker_symbol}: {e}")
    
    # 3. Fallback to nearest in cache if yfinance fails
    if result:
        return result.rate
        
    # Final fallback: return 1.0 (though this should be avoided)
    return Decimal("1.0")

def validate_transaction_price(symbol: str, transaction_date: date, price: Decimal) -> bool:
    """
    Validates if the entered price is within a reasonable range (+/- 10%) of the 
    historical high/low for that day using yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        # For validation, we need the high/low of that specific day
        start_date = transaction_date
        end_date = transaction_date + timedelta(days=1)
        hist = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        if hist.empty:
            return True # Cannot validate, so we accept (or we could warn)
            
        day_low = Decimal(str(hist['Low'].iloc[0]))
        day_high = Decimal(str(hist['High'].iloc[0]))
        
        # Add 10% buffer
        buffer = Decimal("0.10")
        min_allowed = day_low * (Decimal("1.0") - buffer)
        max_allowed = day_high * (Decimal("1.0") + buffer)
        
        return min_allowed <= price <= max_allowed
    except Exception as e:
        print(f"Error validating price for {symbol}: {e}")
        return True # Fallback to true if API fails

def get_current_price(db: Session, asset: Asset) -> Decimal:
    """
    Fetch the latest market price for an asset.
    - For STOCK, use yfinance.
    - For others, use the last transaction price as the "current" price.
    """
    if asset.type == AssetType.STOCK:
        try:
            ticker = yf.Ticker(asset.symbol)
            # Use 'fast_info' for quick access to the latest price if available, 
            # otherwise use the last closing price.
            # In newer yfinance versions, 'fast_info' is a good source for 'last_price'.
            price = Decimal(str(ticker.fast_info['last_price']))
            if price > 0:
                return price
        except Exception as e:
            print(f"Error fetching current price for {asset.symbol}: {e}")
            # Fallback to history
            try:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    return Decimal(str(hist['Close'].iloc[-1]))
            except:
                pass

    # Fallback for all assets: use the last transaction price from the database
    # Join Asset with Transaction, filter by asset_id, sort by date desc
    from src.database.models import Transaction
    stmt = (
        select(Transaction.price_base)
        .where(Transaction.asset_id == asset.id, Transaction.is_deleted == False)
        .order_by(Transaction.date.desc())
        .limit(1)
    )
    last_price = db.execute(stmt).scalar_one_or_none()
    
    if last_price:
        return Decimal(str(last_price))
    
    return Decimal("0")

from datetime import timedelta
