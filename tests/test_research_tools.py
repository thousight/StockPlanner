import pytest
from unittest.mock import patch, MagicMock
from src.tools.news import get_stock_news, web_search
from src.tools.research import get_stock_financials

@patch('src.tools.research.yf.Ticker')
def test_get_stock_financials(mock_ticker_class):
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "trailingPE": 25.0,
        "marketCap": 2800000000000,
        "trailingEps": 6.5,
        "shortName": "Apple Inc."
    }
    mock_ticker_class.return_value = mock_ticker
    
    result = get_stock_financials("AAPL")
    
    assert "Financial Data for AAPL" in result
    assert "25.0" in result
    assert "2,800,000,000,000" in result
    assert "6.5" in result

@patch('src.tools.news.fetch_yfinance_news_urls')
@patch('src.tools.news.get_summary_result')
def test_get_stock_news(mock_summary, mock_urls):
    mock_urls.return_value = [
        {"link": "http://test.com/1", "title": "News 1"}
    ]
    mock_summary.return_value = {
        "title": "News 1",
        "url": "http://test.com/1",
        "summary": "This is a summary of news 1"
    }
    
    result = get_stock_news("AAPL")
    
    assert "News for AAPL" in result
    assert "News 1" in result
    assert "This is a summary of news 1" in result
