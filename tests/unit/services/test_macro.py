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
async def test_calendar_service_mock_fallback():
    with patch("src.config.settings.FINNHUB_API_KEY", None):
        service = EconomicCalendarService()
        events = await service.get_upcoming_events()
        assert len(events) > 0
        assert "event" in events[0]

@pytest.mark.asyncio
async def test_calendar_service_api_call():
    with patch("src.config.settings.FINNHUB_API_KEY", "fake_key"), \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "economicCalendar": [
                {"country": "US", "impact": "high", "event": "NFP", "time": "2024-03-08"},
                {"country": "EU", "impact": "high", "event": "ECB", "time": "2024-03-09"},
                {"country": "US", "impact": "low", "event": "Minor Data", "time": "2024-03-10"}
            ]
        }
        mock_get.return_value = mock_response
        
        service = EconomicCalendarService()
        events = await service.get_upcoming_events()
        
        # Should filter for US and high impact only
        assert len(events) == 1
        assert events[0]["event"] == "NFP"
        mock_get.assert_called_once()
