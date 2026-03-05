import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.tools.sec import (
    extract_section, 
    get_sec_filing_section, 
    get_cached_section, 
    save_to_cache
)

def test_extract_section_risk_factors():
    with open("tests/fixtures/sec/AAPL_10K.html", "r") as f:
        html_content = f.read()
    
    # In a real scenario, section_id might be "item1a" or a regex
    content = extract_section(html_content, "item1a")
    assert "Risk Factors" in content
    assert "iPhones" in content

def test_extract_section_mda():
    with open("tests/fixtures/sec/AAPL_10K.html", "r") as f:
        html_content = f.read()
    
    content = extract_section(html_content, "item7")
    assert "Management's Discussion" in content
    assert "services revenue" in content

def test_extract_section_not_found():
    html_content = "<html><body>Nothing here</body></html>"
    content = extract_section(html_content, "nonexistent")
    assert content == ""

@pytest.mark.asyncio
async def test_get_sec_filing_section_cached(mocker):
    # Mock cache hit
    mocker.patch("src.graph.tools.sec.get_cached_section", return_value="Cached Risk Factors")
    
    content = await get_sec_filing_section("AAPL", "10-K", "item1a")
    assert content == "Cached Risk Factors"

@pytest.mark.asyncio
async def test_get_sec_filing_section_fresh(mocker):
    # Mock cache miss
    mocker.patch("src.graph.tools.sec.get_cached_section", return_value=None)
    # Mock fetch_filing_content
    mocker.patch("src.graph.tools.sec.fetch_filing_content", return_value="<html><div id='item1a'>Fresh Content</div></html>")
    # Mock save_to_cache
    mock_save = mocker.patch("src.graph.tools.sec.save_to_cache")
    
    content = await get_sec_filing_section("AAPL", "10-K", "item1a")
    assert "Fresh Content" in content
    assert mock_save.called

@pytest.mark.asyncio
async def test_get_cached_section_research_hit():
    with patch("src.graph.tools.sec.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_cached = MagicMock()
        mock_cached.content = "Research Cache Content"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_cached, None]
        mock_session.execute.return_value = mock_result
        
        result = await get_cached_section("AAPL", "123", "item1a")
        assert result == "Research Cache Content"

@pytest.mark.asyncio
async def test_get_cached_section_legacy_hit():
    with patch("src.graph.tools.sec.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_cached_legacy = MagicMock()
        mock_cached_legacy.content = "Legacy SEC Content"
        
        mock_result = MagicMock()
        # First call (ResearchCache) returns None, second call (SECCache) returns mock_cached_legacy
        mock_result.scalar_one_or_none.side_effect = [None, mock_cached_legacy]
        mock_session.execute.return_value = mock_result
        
        result = await get_cached_section("AAPL", "123", "item1a")
        assert result == "Legacy SEC Content"

@pytest.mark.asyncio
async def test_save_to_cache_both(mocker):
    with patch("src.graph.tools.sec.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        await save_to_cache("AAPL", "123", "10-K", datetime.now(), "item1a", "New Content")
        # Should call session.add twice (one for ResearchCache, one for SECCache)
        assert mock_session.add.call_count == 2
        assert mock_session.commit.called
