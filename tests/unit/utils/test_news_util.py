import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.utils.news import get_summary, summarize_content
from src.database.models import ResearchCache, ResearchSourceType

@pytest.mark.asyncio
async def test_get_summary_research_cache_hit():
    url = "https://news.com/1"
    
    mock_cached = MagicMock()
    mock_cached.content = "Cached Summary"
    
    with patch("src.graph.utils.news.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cached
        mock_session.execute.return_value = mock_result
        
        result = await get_summary(url)
        assert result == "Cached Summary"

@pytest.mark.asyncio
async def test_get_summary_newscache_fallback():
    url = "https://news.com/2"
    
    with patch("src.graph.utils.news.AsyncSessionLocal") as mock_session_factory, \
         patch("src.graph.utils.news.get_valid_cache", new_callable=AsyncMock) as mock_legacy:
        
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # ResearchCache miss
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Legacy NewsCache hit
        mock_legacy.return_value = "Legacy Summary"
        
        result = await get_summary(url)
        assert result == "Legacy Summary"

@pytest.mark.asyncio
async def test_get_summary_full_flow():
    url = "https://news.com/3"
    
    with patch("src.graph.utils.news.AsyncSessionLocal") as mock_session_factory, \
         patch("src.graph.utils.news.get_valid_cache", new_callable=AsyncMock) as mock_legacy, \
         patch("src.graph.utils.news.fetch_content", new_callable=AsyncMock) as mock_fetch, \
         patch("src.graph.utils.news.clean_html") as mock_clean, \
         patch("src.graph.utils.news.summarize_content", new_callable=AsyncMock) as mock_summ:
        
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # Caches miss
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        mock_legacy.return_value = None
        
        # Fetch flow
        mock_fetch.return_value = "<html>Content</html>"
        mock_clean.return_value = "Cleaned content"
        mock_summ.return_value = "New Summary"
        
        result = await get_summary(url)
        assert result == "New Summary"
        assert mock_session.add.called

@pytest.mark.asyncio
async def test_summarize_content_short():
    assert await summarize_content("too short", "url") is None

@pytest.mark.asyncio
async def test_summarize_content_llm_call():
    content = "This is a long enough content to summarize for the test purpose." * 10
    
    with patch("langchain_openai.ChatOpenAI.ainvoke", new_callable=AsyncMock) as mock_invoke:
        mock_res = MagicMock()
        mock_res.content = "LLM Summary"
        mock_invoke.return_value = mock_res
        
        result = await summarize_content(content, "https://url.com")
        assert result == "LLM Summary"
