import pytest
from unittest.mock import AsyncMock, patch
from src.graph.tools.sec import get_sec_filing_section, get_sec_filing_delta

@pytest.mark.asyncio
async def test_get_sec_filing_section_integration(mocker):
    # Mocking external hits
    mocker.patch("src.graph.tools.sec.fetch_filing_content", return_value="<html><div id='item1a'>Integrated Risk Factors</div></html>")
    mocker.patch("src.graph.tools.sec.get_cached_section", return_value=None)
    mocker.patch("src.graph.tools.sec.save_to_cache", return_value=None)
    
    result = await get_sec_filing_section("AAPL", "10-K", "item1a")
    assert "Integrated Risk Factors" in result

@pytest.mark.asyncio
async def test_get_sec_filing_delta_integration(mocker):
    # Mocking the tools used inside delta
    mocker.patch("src.graph.tools.sec.get_sec_filing_section", return_value="Current Section Content")
    
    # Mock LLM chain invoke
    mock_response = AsyncMock()
    mock_response.content = "Semantic Delta: New risk added regarding AI competition."
    
    with patch("langchain_core.runnables.base.RunnableSequence.ainvoke", return_value=mock_response):
        result = await get_sec_filing_delta("AAPL", "10-K", "item1a")
        assert "Semantic Delta" in result
        assert "AI competition" in result
