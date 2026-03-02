from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
import yfinance as yf
from src.schemas.portfolio import BenchmarkComparison

async def get_spy_performance(db: AsyncSession, portfolio_gain_pct: Decimal) -> BenchmarkComparison:
    """
    Fetch SPY performance for benchmarking.
    For simplicity in this MVP, we compare against the Year-to-Date (YTD) performance of SPY.
    """
    benchmark_name = "S&P 500 (SPY)"
    try:
        spy = yf.Ticker("SPY")
        # Get YTD performance
        # Note: yfinance history() is synchronous
        hist = spy.history(period="ytd")
        if not hist.empty:
            start_price = Decimal(str(hist['Close'].iloc[0]))
            end_price = Decimal(str(hist['Close'].iloc[-1]))
            benchmark_gain_pct = (end_price - start_price) / start_price * 100
        else:
            benchmark_gain_pct = Decimal("0")
    except Exception as e:
        print(f"Error fetching SPY data: {e}")
        benchmark_gain_pct = Decimal("0")
        
    return BenchmarkComparison(
        benchmark_name=benchmark_name,
        portfolio_gain_pct=portfolio_gain_pct,
        benchmark_gain_pct=benchmark_gain_pct,
        relative_performance=portfolio_gain_pct - benchmark_gain_pct
    )
