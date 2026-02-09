"""
Unit tests for research utils functions.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock


class TestParseYfNewsItem:
    """Tests for _parse_yf_news_item function."""
    
    def test_parse_new_yfinance_structure(self):
        """Test parsing news item with nested content structure."""
        from src.agents.nodes.research.utils import _parse_yf_news_item
        
        item = {
            "content": {
                "title": "Apple announces new product",
                "clickThroughUrl": {"url": "https://example.com/apple-news"}
            }
        }
        
        result = _parse_yf_news_item(item)
        
        assert result is not None
        assert result["title"] == "Apple announces new product"
        assert result["link"] == "https://example.com/apple-news"
    
    def test_parse_new_yfinance_with_canonical_url(self):
        """Test parsing with canonicalUrl when clickThroughUrl is missing."""
        from src.agents.nodes.research.utils import _parse_yf_news_item
        
        item = {
            "content": {
                "title": "Market Update",
                "canonicalUrl": {"url": "https://example.com/market"}
            }
        }
        
        result = _parse_yf_news_item(item)
        
        assert result is not None
        assert result["link"] == "https://example.com/market"
    
    def test_parse_old_yfinance_structure(self):
        """Test parsing news item with flat structure."""
        from src.agents.nodes.research.utils import _parse_yf_news_item
        
        item = {
            "title": "Stock Update",
            "link": "https://example.com/stock"
        }
        
        result = _parse_yf_news_item(item)
        
        assert result is not None
        assert result["title"] == "Stock Update"
        assert result["link"] == "https://example.com/stock"
    
    def test_parse_invalid_item_returns_none(self):
        """Test that invalid items return None."""
        from src.agents.nodes.research.utils import _parse_yf_news_item
        
        item = {"random": "data"}
        result = _parse_yf_news_item(item)
        
        assert result is None
    
    def test_parse_missing_link_returns_none(self):
        """Test that items without link return None."""
        from src.agents.nodes.research.utils import _parse_yf_news_item
        
        item = {"content": {"title": "No Link News"}}
        result = _parse_yf_news_item(item)
        
        assert result is None


class TestGetSummaryResult:
    """Tests for get_summary_result function."""
    
    @patch('src.agents.nodes.research.utils.get_summary')
    def test_returns_title_and_summary(self, mock_get_summary):
        """Test successful summary result."""
        from src.agents.nodes.research.utils import get_summary_result
        
        mock_get_summary.return_value = "This is a summary"
        item = {"title": "News Title", "link": "https://example.com"}
        
        result = get_summary_result(item)
        
        assert result == {"title": "News Title", "summary": "This is a summary"}
    
    @patch('src.agents.nodes.research.utils.get_summary')
    def test_returns_none_when_no_summary(self, mock_get_summary):
        """Test returns None when summary fails."""
        from src.agents.nodes.research.utils import get_summary_result
        
        mock_get_summary.return_value = None
        item = {"title": "News Title", "link": "https://example.com"}
        
        result = get_summary_result(item)
        
        assert result is None


class TestFetchYfinanceNewsUrls:
    """Tests for fetch_yfinance_news_urls function."""
    
    @patch('src.agents.nodes.research.utils.yf.Ticker')
    def test_fetches_news_urls(self, mock_ticker_class):
        """Test successful news URL fetching."""
        from src.agents.nodes.research.utils import fetch_yfinance_news_urls
        
        mock_ticker = MagicMock()
        mock_ticker.news = [
            {"title": "News 1", "link": "https://example.com/1"},
            {"title": "News 2", "link": "https://example.com/2"},
        ]
        mock_ticker_class.return_value = mock_ticker
        
        results = fetch_yfinance_news_urls("AAPL")
        
        assert len(results) == 2
        assert results[0]["title"] == "News 1"
    
    @patch('src.agents.nodes.research.utils.yf.Ticker')
    def test_handles_empty_news(self, mock_ticker_class):
        """Test handling when no news is available."""
        from src.agents.nodes.research.utils import fetch_yfinance_news_urls
        
        mock_ticker = MagicMock()
        mock_ticker.news = None
        mock_ticker_class.return_value = mock_ticker
        
        results = fetch_yfinance_news_urls("AAPL")
        
        assert results == []
    
    @patch('src.agents.nodes.research.utils.yf.Ticker')
    def test_handles_exception(self, mock_ticker_class):
        """Test graceful handling of exceptions."""
        from src.agents.nodes.research.utils import fetch_yfinance_news_urls
        
        mock_ticker_class.side_effect = Exception("API Error")
        
        results = fetch_yfinance_news_urls("AAPL")
        
        assert results == []


class TestFetchDdgsUrls:
    """Tests for fetch_ddgs_urls function."""
    
    @patch('src.agents.nodes.research.utils.DDGS')
    def test_fetches_search_results(self, mock_ddgs_class):
        """Test successful search result fetching."""
        from src.agents.nodes.research.utils import fetch_ddgs_urls
        
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = Mock(return_value=False)
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "href": "https://example.com/1"},
            {"title": "Result 2", "href": "https://example.com/2"},
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        results = fetch_ddgs_urls("test query")
        
        assert len(results) == 2
        assert results[0]["title"] == "Result 1"
        assert results[0]["link"] == "https://example.com/1"
    
    @patch('src.agents.nodes.research.utils.DDGS')
    def test_handles_exception(self, mock_ddgs_class):
        """Test graceful handling of exceptions."""
        from src.agents.nodes.research.utils import fetch_ddgs_urls
        
        mock_ddgs_class.side_effect = Exception("Search Error")
        
        results = fetch_ddgs_urls("test query")
        
        assert results == []


class TestFetchArticleContent:
    """Tests for fetch_article_content function."""
    
    @patch('src.agents.nodes.research.utils.requests.get')
    def test_fetches_and_extracts_content(self, mock_get):
        """Test successful content extraction."""
        from src.agents.nodes.research.utils import fetch_article_content
        
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <h1>Main Heading</h1>
                    <p>This is the main content of the article with important information.</p>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = fetch_article_content("https://example.com/article")
        
        assert "Main Heading" in result or "main content" in result.lower()
        mock_get.assert_called_once()
    
    @patch('src.agents.nodes.research.utils.requests.get')
    def test_handles_request_error(self, mock_get):
        """Test handling of request errors."""
        from src.agents.nodes.research.utils import fetch_article_content
        
        mock_get.side_effect = Exception("Connection Error")
        
        result = fetch_article_content("https://example.com/article")
        
        assert result == ""
    
    @patch('src.agents.nodes.research.utils.requests.get')
    def test_handles_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        from src.agents.nodes.research.utils import fetch_article_content
        from requests.exceptions import HTTPError
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = fetch_article_content("https://example.com/missing")
        
        assert result == ""


class TestSummarizeContent:
    """Tests for summarize_content function."""
    
    @patch('src.agents.nodes.research.utils.ChatOpenAI')
    def test_summarizes_content(self, mock_llm_class):
        """Test successful content summarization."""
        from src.agents.nodes.research.utils import summarize_content
        
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "This is a summary of the article."
        mock_llm_class.return_value = mock_llm
        
        content = "A" * 200  # Content longer than 100 chars
        result = summarize_content(content, "https://example.com")
        
        assert result == "This is a summary of the article."
    
    def test_returns_none_for_short_content(self):
        """Test that short content returns None."""
        from src.agents.nodes.research.utils import summarize_content
        
        result = summarize_content("Short", "https://example.com")
        
        assert result is None
    
    def test_returns_none_for_empty_content(self):
        """Test that empty content returns None."""
        from src.agents.nodes.research.utils import summarize_content
        
        result = summarize_content("", "https://example.com")
        
        assert result is None
    
    @patch('src.agents.nodes.research.utils.ChatOpenAI')
    def test_handles_llm_error(self, mock_llm_class):
        """Test handling of LLM errors."""
        from src.agents.nodes.research.utils import summarize_content
        
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_llm_class.return_value = mock_llm
        
        content = "A" * 200
        result = summarize_content(content, "https://example.com")
        
        assert result == "Error generating summary."


class TestGetSummary:
    """Tests for get_summary function."""
    
    @patch('src.agents.nodes.research.utils.SessionLocal')
    @patch('src.agents.nodes.research.utils.get_valid_cache')
    def test_returns_cached_summary(self, mock_cache, mock_session):
        """Test returning cached summary."""
        from src.agents.nodes.research.utils import get_summary
        
        mock_cache.return_value = "Cached summary"
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        result = get_summary("https://example.com")
        
        assert result == "Cached summary"
    
    @patch('src.agents.nodes.research.utils.SessionLocal')
    @patch('src.agents.nodes.research.utils.get_valid_cache')
    @patch('src.agents.nodes.research.utils.fetch_article_content')
    @patch('src.agents.nodes.research.utils.summarize_content')
    @patch('src.agents.nodes.research.utils.save_cache')
    def test_fetches_and_caches_on_miss(self, mock_save, mock_summarize, mock_fetch, mock_cache, mock_session):
        """Test fetching and caching on cache miss."""
        from src.agents.nodes.research.utils import get_summary
        
        mock_cache.return_value = None  # Cache miss
        mock_fetch.return_value = "Article content"
        mock_summarize.return_value = "New summary"
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        result = get_summary("https://example.com")
        
        assert result == "New summary"
        mock_save.assert_called_once()
    
    def test_returns_none_for_empty_url(self):
        """Test that empty URL returns None."""
        from src.agents.nodes.research.utils import get_summary
        
        result = get_summary("")
        
        assert result is None


class TestResolveSymbol:
    """Tests for resolve_symbol function."""
    
    @patch('src.agents.nodes.research.utils.yf.Ticker')
    @patch('src.agents.nodes.research.utils.get_current_price')
    @patch('src.agents.nodes.research.utils.get_stock_news')
    @patch('src.agents.nodes.research.utils.get_company_info')
    def test_returns_symbol_data(self, mock_info, mock_news, mock_price, mock_ticker):
        """Test successful symbol resolution."""
        from src.agents.nodes.research.utils import resolve_symbol
        
        mock_price.return_value = 150.0
        mock_news.return_value = [{"title": "News", "summary": "Summary"}]
        mock_info.return_value = {"pe_ratio": 25.0}
        
        result = resolve_symbol("AAPL")
        
        assert result["current_price"] == 150.0
        assert result["news"] == [{"title": "News", "summary": "Summary"}]
        assert result["info"] == {"pe_ratio": 25.0}
    
    @patch('src.agents.nodes.research.utils.yf.Ticker')
    def test_handles_exception(self, mock_ticker):
        """Test graceful handling of exceptions."""
        from src.agents.nodes.research.utils import resolve_symbol
        
        mock_ticker.side_effect = Exception("API Error")
        
        result = resolve_symbol("INVALID")
        
        assert result["current_price"] == 0
        assert result["news"] == []
        assert result["info"] == {}


class TestGetCompanyInfo:
    """Tests for get_company_info function."""
    
    def test_returns_company_data(self):
        """Test successful company info retrieval."""
        from src.agents.nodes.research.utils import get_company_info
        
        mock_stock = MagicMock()
        mock_stock.ticker = "AAPL"
        mock_stock.info = {
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "marketCap": 3000000000000,
            "trailingPE": 28.5,
            "pegRatio": 2.1,
            "trailingEps": 6.5,
            "recommendationKey": "buy"
        }
        mock_stock.calendar = MagicMock()
        mock_stock.calendar.empty = True
        
        result = get_company_info(mock_stock)
        
        assert result["symbol"] == "AAPL"
        assert result["sector"] == "Technology"
        assert result["market_cap"] == 3000000000000
        assert result["pe_ratio"] == 28.5
        assert result["analyst_rating"] == "buy"
    
    def test_handles_missing_info(self):
        """Test handling when info is missing."""
        from src.agents.nodes.research.utils import get_company_info
        
        mock_stock = MagicMock()
        mock_stock.ticker = "TEST"
        mock_stock.info = {}
        mock_stock.calendar = None
        
        result = get_company_info(mock_stock)
        
        assert result["symbol"] == "TEST"
        assert result["sector"] == "Unknown"
        assert result["market_cap"] == 0
