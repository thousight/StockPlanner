from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import FXRate, Asset, AssetType, Transaction, RecordStatus
import yfinance as yf

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
        ticker = yf.Ticker(ticker_symbol)
        # Fetch data for a range around the date
        hist = ticker.history(start=transaction_date.strftime('%Y-%m-%d'), end=(transaction_date + timedelta(days=1)).strftime('%Y-%m-%d'))
        
        if hist.empty:
            hist = ticker.history(period="5d")
        
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

def validate_transaction_price(symbol: str, transaction_date: date, price: Decimal) -> bool:
    """
    Validates if the entered price is within a reasonable range (+/- 10%) of the 
    historical high/low for that day using yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        start_date = transaction_date
        end_date = transaction_date + timedelta(days=1)
        hist = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
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
        try:
            ticker = yf.Ticker(asset.symbol)
            price = Decimal(str(ticker.fast_info['last_price']))
            if price > 0:
                return price
        except Exception as e:
            print(f"Error fetching current price for {asset.symbol}: {e}")
            try:
                hist = ticker.history(period="1d")
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
