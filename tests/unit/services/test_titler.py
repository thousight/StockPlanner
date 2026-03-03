import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.titler import generate_thread_title, update_thread_title_background
from src.database.models import ChatThread

@pytest.mark.asyncio
async def test_generate_thread_title_success():
    with patch("src.services.titler.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        
        mock_response = MagicMock(content="Apple Stock Analysis")
        # Use AsyncMock for ainvoke
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        title = await generate_thread_title("Help with AAPL", "I've researched Apple.")
        assert title == "Apple Stock Analysis"

@pytest.mark.asyncio
async def test_generate_thread_title_fallback():
    with patch("src.services.titler.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("Service Down"))
        
        title = await generate_thread_title("Help", "OK")
        assert title == "New Chat"

@pytest.mark.asyncio
async def test_update_thread_title_background():
    # Mock database session and query
    mock_thread = ChatThread(id="thread1", title="Old")
    
    with patch("src.services.titler.generate_thread_title", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Updated Title"
        
        with patch("src.services.titler.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_thread
            mock_session.execute.return_value = mock_result
            
            await update_thread_title_background("thread1", "User", "AI")
            
            assert mock_thread.title == "Updated Title"
            assert mock_session.commit.called
