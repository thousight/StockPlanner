import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.utils.scraping import fetch_content, clean_html

@pytest.mark.asyncio
async def test_fetch_content_success():
    url = "https://example.com"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>Hello World</h1></body></html>"
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await fetch_content(url)
        assert "Hello World" in result

@pytest.mark.asyncio
async def test_fetch_content_failure():
    url = "https://example.com/404"
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await fetch_content(url)
        assert result == ""

@pytest.mark.asyncio
async def test_fetch_content_empty_url():
    assert await fetch_content("") == ""
    assert await fetch_content(None) == ""

@pytest.mark.asyncio
async def test_fetch_content_exception():
    with patch("httpx.AsyncClient.get", side_effect=Exception("Network error")):
        result = await fetch_content("https://error.com")
        assert result == ""

def test_clean_html_basic():
    html = "<html><body><header>Nav</header><main><h1>Title</h1><p>Main content here.</p></main><footer>Footer</footer></body></html>"
    # readability-lxml should extract the main content
    result = clean_html(html)
    assert "Title" in result
    assert "Main content here" in result
    assert "Nav" not in result
    assert "Footer" not in result

def test_clean_html_empty():
    assert clean_html("") == ""
    assert clean_html(None) == ""

def test_clean_html_exception():
    with patch("src.graph.utils.scraping.Document", side_effect=Exception("Parsing error")):
        assert clean_html("<html></html>") == ""
