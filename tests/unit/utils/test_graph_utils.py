import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage
from src.graph.utils.prompt import convert_state_to_prompt, convert_tools_to_prompt
from src.graph.utils.agents import with_logging, get_next_interaction_id
from src.graph.utils.news import get_summary_result

def test_convert_state_to_prompt_empty():
    state = {}
    result = convert_state_to_prompt(state)
    assert "Chat History: None." in result
    assert "Agent Interactions: None." in result

def test_convert_state_to_prompt_complex():
    state = {
        "user_input": "What is AAPL price?",
        "session_context": {
            "current_datetime": "2023-01-01 12:00:00",
            "messages": [
                HumanMessage(content="Hello"),
                ("ai", "Hi there!"),
                AIMessage(content="How can I help?")
            ],
            "revision_count": 1
        },
        "agent_interactions": [
            {"agent": "supervisor", "answer": "Consulting analyst", "next_agent": "analyst"}
        ],
        "user_context": {
            "portfolio_summary": "User owns 10 shares of AAPL"
        }
    }
    result = convert_state_to_prompt(state)
    assert "User Input: What is AAPL price?" in result
    assert "Current Date/Time: 2023-01-01 12:00:00" in result
    assert "User: Hello" in result
    assert "AI: Hi there!" in result
    assert "AI: How can I help?" in result
    assert "[supervisor -> analyst]: Consulting analyst" in result
    assert "Revision Count: 1" in result
    assert "User owns 10 shares of AAPL" in result

def test_convert_tools_to_prompt():
    def my_tool(arg1: str, arg2: int = 10):
        """This is my tool.
        More details here.
        """
        pass
    
    result = convert_tools_to_prompt([my_tool])
    assert "- my_tool(arg1: str, arg2: int = 10): This is my tool." in result

@pytest.mark.asyncio
async def test_with_logging_async_success():
    mock_func = AsyncMock()
    mock_func.__name__ = "test_agent"
    
    decorated = with_logging(mock_func)
    
    with patch("src.graph.utils.agents.logger") as mock_logger:
        await decorated(state={"foo": "bar"}, config={"configurable": {"thread_id": "123"}})
        
        # print(f"DEBUG info calls: {mock_logger.info.call_args_list}")
        assert mock_logger.info.called
        # Check case-insensitively or for 'Starting'
        assert any("Starting" in str(call) for call in mock_logger.info.call_args_list)
        mock_func.assert_called_once()

@pytest.mark.asyncio
async def test_with_logging_async_failure():
    async def failing_agent(*args, **kwargs):
        raise ValueError("Boom")
    
    decorated = with_logging(failing_agent)
    
    with patch("src.graph.utils.agents.logger") as mock_logger:
        with pytest.raises(ValueError, match="Boom"):
            await decorated(state={}, config={})
        
        assert mock_logger.error.called

def test_get_next_interaction_id():
    state = {"agent_interactions": [{}, {}]}
    assert get_next_interaction_id(state) == 3
    assert get_next_interaction_id({}) == 1

@pytest.mark.asyncio
async def test_get_summary_result_mapping():
    item = {"title": "T", "link": "L", "user_agent": "UA"}
    
    with patch("src.graph.utils.news.get_summary", new_callable=AsyncMock) as mock_sum:
        mock_sum.return_value = "S"
        
        result = await get_summary_result(item)
        assert result == {"title": "T", "summary": "S", "url": "L"}
        mock_sum.assert_called_with("L", "UA", expire_at=None)
