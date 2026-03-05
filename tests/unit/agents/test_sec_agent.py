import pytest
from unittest.mock import AsyncMock, patch
from src.graph.tools.sec import extract_section, get_sec_filing_section

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
