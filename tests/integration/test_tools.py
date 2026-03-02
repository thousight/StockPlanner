import pytest
import pandas as pd
from unittest.mock import MagicMock, AsyncMock, patch
from src.graph.tools.research import get_stock_financials
from src.graph.tools.news import get_stock_news, get_macro_economic_news, web_search

@pytest.fixture
def mock_ticker_data():
    mock = MagicMock()
    mock.info = {
        "trailingPE": 15.5,
        "marketCap": 2000000000,
        "trailingEps": 5.2,
        "totalRevenue": 5000000000,
        "profitMargins": 0.12,
        "longBusinessSummary": "Mock business summary."
    }
    mock.history.return_value = pd.DataFrame({"Close": [100.0, 105.0]}, index=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")])
    mock.news = [
        {
            "content": {
                "title": "Mock News Title",
                "clickThroughUrl": {"url": "https://example.com/mock-news"}
            }
        }
    ]
    return mock

@pytest.mark.asyncio
async def test_get_stock_financials(mock_ticker_data):
    with patch("src.graph.tools.research.yf.Ticker", return_value=mock_ticker_data):
        result = get_stock_financials("AAPL")
        assert "**Financial Data for AAPL**" in result
        assert "Market Cap: $2,000,000,000" in result
        assert "P/E Ratio: 15.5" in result
        assert "Business Summary: Mock business summary." in result

@pytest.mark.asyncio
async def test_get_stock_news(mock_ticker_data):
    with patch("src.graph.tools.news.yf.Ticker", return_value=mock_ticker_data), \
         patch("src.graph.utils.news.get_summary", new_callable=AsyncMock) as mock_get_summary:
        mock_get_summary.return_value = "Mock summary content."
        result = await get_stock_news("AAPL")
        assert "News for AAPL:" in result
        assert "**Mock News Title**: Mock summary content." in result

@pytest.mark.asyncio
async def test_get_macro_economic_news(mock_ticker_data):
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = [
        {"title": "Mock DDG Title", "href": "https://example.com/mock-ddg"}
    ]
    
    with patch("src.graph.utils.news.yf.Ticker", return_value=mock_ticker_data), \
         patch("src.graph.utils.news.DDGS") as mock_ddgs_class, \
         patch("src.graph.utils.news.get_summary", new_callable=AsyncMock) as mock_get_summary:
        
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs_instance
        mock_get_summary.return_value = "Mock summary content."
        
        result = await get_macro_economic_news()
        assert "Macro Economic News:" in result
        assert "Mock News Title" in result
        assert "Mock DDG Title" in result

@pytest.mark.asyncio
async def test_web_search():
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = [
        {"title": "Mock DDG Title", "href": "https://example.com/mock-ddg"}
    ]
    
    with patch("src.graph.utils.news.DDGS") as mock_ddgs_class, \
         patch("src.graph.utils.news.get_summary", new_callable=AsyncMock) as mock_get_summary:
        
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs_instance
        mock_get_summary.return_value = "Mock summary content."
        
        result = await web_search(["test query"])
        assert "Web Search Results:" in result
        assert "Query: 'test query'" in result
        assert "Mock DDG Title" in result

@pytest.mark.asyncio
async def test_get_stock_financials_error():
    with patch("src.graph.tools.research.yf.Ticker", side_effect=Exception("API Error")):
        result = get_stock_financials("AAPL")
        assert "Failed to fetch financial data for AAPL: API Error" in result

@pytest.mark.asyncio
async def test_get_stock_news_no_results(mock_ticker_data):
    mock_ticker_data.news = []
    with patch("src.graph.tools.news.yf.Ticker", return_value=mock_ticker_data):
        result = await get_stock_news("AAPL")
        assert result is None
