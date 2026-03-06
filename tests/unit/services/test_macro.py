import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.macro import FEDService, EconomicCalendarService

@pytest.mark.asyncio
async def test_fed_service_mock_fallback():
    with patch("src.config.settings.FRED_API_KEY", None):
        service = FEDService()
        data = await service.get_series_data("GDP", limit=2)
        assert len(data) == 2
        assert "date" in data[0]
        assert "value" in data[0]

@pytest.mark.asyncio
async def test_fed_service_api_call():
    with patch("src.config.settings.FRED_API_KEY", "fake_key"), \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "observations": [
                {"date": "2024-01-01", "value": "3.5"}
            ]
        }
        mock_get.return_value = mock_response
        
        service = FEDService()
        data = await service.get_series_data("GDP", limit=1)
        
        assert len(data) == 1
        assert data[0]["value"] == "3.5"
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_calendar_service_fred_api_call():
    with patch("src.config.settings.FRED_API_KEY", "fake_fred_key"), \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        # FRED releases/dates response structure
        mock_response.json.return_value = {
            "release_dates": [
                {"release_id": 10, "date": "2024-03-08", "release_name": "Consumer Price Index"},
                {"release_id": 53, "date": "2024-03-28", "release_name": "Gross Domestic Product"},
                {"release_id": 999, "date": "2024-03-10", "release_name": "Ignore Me"}
            ]
        }
        mock_get.return_value = mock_response
        
        service = EconomicCalendarService()
        events = await service.get_upcoming_events()
        
        # Should filter for important release IDs (10 and 53)
        assert len(events) == 2
        event_names = [e["event"] for e in events]
        assert "Consumer Price Index (CPI)" in event_names
        assert "Gross Domestic Product (GDP)" in event_names
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_calendar_service_fallback_on_error():
    with patch("src.config.settings.FRED_API_KEY", "fake_key"), \
         patch("httpx.AsyncClient.get", side_effect=Exception("Network Error")):
        service = EconomicCalendarService()
        events = await service.get_upcoming_events()
        # Should return mock data
        assert len(events) > 0
        assert "FOMC" in events[0]["event"]
