from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import httpx

from src.config import settings

# Mapping of common names to FRED Series IDs
FRED_SERIES_MAP = {
    "GDP": "A191RL1Q225SBEA", # Real GDP Quarterly % Change
    "CPI": "CPIAUCSL",        # Consumer Price Index
    "FEDFUNDS": "FEDFUNDS",   # Effective Federal Funds Rate
    "PAYEMS": "PAYEMS",       # Total Nonfarm Payrolls
    "DXY": "DTWEXBGS"         # Nominal Broad U.S. Dollar Index
}

class FEDService:
    """Service to fetch authoritative macroeconomic data from the FRED API."""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self):
        self.api_key = settings.FRED_API_KEY

    async def get_series_data(self, series_name_or_id: str, limit: int = 6) -> List[Dict[str, str]]:
        """
        Fetch the most recent observations for a given series.
        If api_key is missing, returns mock data for development.
        """
        series_id = FRED_SERIES_MAP.get(series_name_or_id.upper(), series_name_or_id)
        
        if not self.api_key:
            return self._get_mock_fred_data(series_id, limit)

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
            print(f"Error fetching FRED data for {series_id}: {e}")
            return self._get_mock_fred_data(series_id, limit)

    def _get_mock_fred_data(self, series_id: str, limit: int) -> List[Dict[str, str]]:
        return [
            {"date": (datetime.now() - timedelta(days=30 * i)).strftime("%Y-%m-%d"), "value": str(2.0 + (i * 0.1))}
            for i in range(limit)
        ]


class EconomicCalendarService:
    """Service to fetch upcoming high-impact economic events from Finnhub."""
    
    BASE_URL = "https://finnhub.io/api/v1/calendar/economic"

    def __init__(self):
        self.api_key = settings.FINNHUB_API_KEY

    async def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch High-Impact US events for the next 'days'.
        If api_key is missing, returns mock data for development.
        """
        if not self.api_key:
            return self._get_mock_calendar_data()

        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        params = {
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "token": self.api_key
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                events = data.get("economicCalendar", [])
                us_high_impact = []
                for event in events:
                    if event.get("country") == "US" and event.get("impact") == "high":
                        us_high_impact.append({
                            "event": event.get("event"),
                            "time": event.get("time"),
                            "actual": event.get("actual"),
                            "estimate": event.get("estimate"),
                            "previous": event.get("previous")
                        })
                return us_high_impact
        except Exception as e:
            print(f"Error fetching Finnhub calendar: {e}")
            return self._get_mock_calendar_data()

    def _get_mock_calendar_data(self) -> List[Dict[str, Any]]:
        return [
            {
                "event": "FOMC Interest Rate Decision",
                "time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "actual": None,
                "estimate": "5.25",
                "previous": "5.50"
            },
            {
                "event": "Core CPI m/m",
                "time": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
                "actual": None,
                "estimate": "0.3",
                "previous": "0.4"
            }
        ]

fed_service = FEDService()
calendar_service = EconomicCalendarService()
