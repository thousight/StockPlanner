import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.agents.supervisor.agent import supervisor_agent
from src.graph.agents.supervisor.response import SupervisorResponse

@pytest.mark.asyncio
async def test_supervisor_parallel_routing():
    state = {
        "user_input": "Analyze AAPL fundamentals and sentiment",
        "agent_interactions": [],
        "session_context": {"revision_count": 0}
    }
    
    # Mock LLM response with multiple agents
    mock_res = SupervisorResponse(next_agents=["fundamental_researcher", "sentiment_researcher"])
    
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_res
        mock_struct.return_value = mock_chain
        
        result = await supervisor_agent(state)
        
        # Check that next_agent string contains both (joined by comma)
        next_agent = result["agent_interactions"][0]["next_agent"]
        assert "fundamental_researcher" in next_agent
        assert "sentiment_researcher" in next_agent
        assert "," in next_agent

@pytest.mark.asyncio
async def test_supervisor_loop_limit():
    state = {
        "user_input": "...",
        "agent_interactions": [],
        "session_context": {"revision_count": 6} # Over limit
    }
    
    result = await supervisor_agent(state)
    assert result["agent_interactions"][0]["next_agent"] == "summarizer"
    assert "Loop limit reached" in result["agent_interactions"][0]["answer"]
