import pandas_market_calendars as mcal
from datetime import date, datetime, timedelta
from typing import Union

def get_previous_trading_day(target_date: Union[date, datetime]) -> date:
    """
    Returns the date of the previous trading day on the NYSE.
    If target_date is a weekend or holiday, it returns the last valid session.
    If target_date is a valid trading day, it still returns the PRIOR session.
    """
    if isinstance(target_date, datetime):
        target_date = target_date.date()
        
    nyse = mcal.get_calendar('NYSE')
    
    # Look back 14 days to ensure we catch a valid session even over long holidays
    start_search = target_date - timedelta(days=14)
    end_search = target_date - timedelta(days=1)
    
    valid_days = nyse.valid_days(start_date=start_search, end_date=end_search)
    
    if valid_days.empty:
        # Log failure instead of silent fallback
        print(f"[ERROR] Could not determine previous trading day for {target_date} using NYSE calendar.")
        # Return literal yesterday as a weak fallback but the tool should know it's a gap
        return target_date - timedelta(days=1)
        
    # valid_days returns a DatetimeIndex in UTC
    return valid_days[-1].date()
