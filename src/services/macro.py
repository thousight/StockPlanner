import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

# Mapping of common names to FRED Series IDs
FRED_SERIES_MAP = {
    "GDP": "A191RL1Q225SBEA", # Real GDP Quarterly % Change
    "CPI": "CPIAUCSL",        # Consumer Price Index
    "FEDFUNDS": "FEDFUNDS",   # Effective Federal Funds Rate
    "PAYEMS": "PAYEMS",       # Total Nonfarm Payrolls
    "DXY": "DTWEXBGS"         # Nominal Broad U.S. Dollar Index
}

# Key FRED Release IDs for the Economic Calendar
# Reference: https://fred.stlouisfed.org/docs/api/fred/releases.html
IMPORTANT_RELEASE_IDS = {
    "10": "Consumer Price Index (CPI)",
    "53": "Gross Domestic Product (GDP)",
    "194": "FOMC Minutes/Projections",
    "50": "Employment Situation (Non-farm Payrolls)",
    "13": "Retail Sales",
    "103": "Consumer Sentiment",
    "94": "Personal Income and Outlays (PCE)",
}

class FEDService:
    """Service to fetch authoritative macroeconomic data from the FRED API."""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self):
        self.api_key = settings.FRED_API_KEY

    async def get_series_data(self, series_name_or_id: str, limit: int = 6) -> List[Dict[str, str]]:
        """
        Fetch the most recent observations for a given series.
        Returns empty list if data retrieval fails or API key is missing.
        """
        series_id = FRED_SERIES_MAP.get(series_name_or_id.upper(), series_name_or_id)
        
        if not self.api_key:
            logger.warning(f"FRED API key missing. Cannot fetch data for {series_id}.")
            return []

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                observations = data.get("observations", [])
                results = []
                for obs in observations:
                    results.append({
                        "date": obs.get("date"),
                        "value": obs.get("value")
                    })
                return results
        except Exception as e:
            logger.error(f"Error fetching FRED data for {series_id}: {e}")
            return []


class EconomicCalendarService:
    """Service to fetch upcoming high-impact economic events from FRED (Authoritative Source)."""
    
    BASE_URL = "https://api.stlouisfed.org/fred/releases/dates"

    def __init__(self):
        self.api_key = settings.FRED_API_KEY

    async def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch high-signal US economic releases for the next 'days' using FRED API.
        """
        if not self.api_key:
            logger.warning("FRED API key missing. Cannot fetch economic calendar.")
            return []

        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        params = {
            "api_key": self.api_key,
            "file_type": "json",
            "realtime_start": start_date.strftime("%Y-%m-%d"),
            "realtime_end": end_date.strftime("%Y-%m-%d"),
            "limit": 1000,
            "include_release_dates_with_no_data": "true" # Essential for seeing future dates
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                all_releases = data.get("release_dates", [])
                high_impact_events = []
                
                for release in all_releases:
                    rid = str(release.get("release_id"))
                    if rid in IMPORTANT_RELEASE_IDS:
                        high_impact_events.append({
                            "event": IMPORTANT_RELEASE_IDS[rid],
                            "time": f"{release.get('date')} (Release ID: {rid})",
                            "actual": None, # FRED releases/dates endpoint doesn't show values
                            "estimate": "Check Report",
                            "previous": "Check Report"
                        })
                
                # Deduplicate by name and date if necessary, sort by date
                high_impact_events.sort(key=lambda x: x["time"])
                
                return high_impact_events
        except Exception as e:
            logger.error(f"Error fetching FRED economic calendar: {e}")
            return []

fed_service = FEDService()
calendar_service = EconomicCalendarService()
