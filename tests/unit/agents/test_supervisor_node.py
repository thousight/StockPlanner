import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.graph.agents.supervisor.agent import supervisor_agent
from src.graph.agents.supervisor.response import SupervisorResponse
from src.graph.state import AgentState

@pytest.fixture
def sample_state() -> AgentState:
    return {
        "session_context": {
            "user_agent": "Test",
            "messages": [],
            "revision_count": 0
        },
        "user_context": {},
        "user_input": "Analyze AAPL",
        "agent_interactions": [],
        "output": ""
    }

@pytest.mark.asyncio
async def test_supervisor_agent_routing(sample_state):
    # Mock LLM to return a routing decision to research
    mock_response = SupervisorResponse(next_agent="research")
    
    with patch("src.graph.agents.supervisor.agent.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        
        mock_structured = AsyncMock()
        mock_structured.ainvoke.return_value = mock_response
        mock_llm.with_structured_output.return_value = mock_structured
        
        result = await supervisor_agent(sample_state)
        
        assert result["agent_interactions"][0]["next_agent"] == "research"
        assert result["agent_interactions"][0]["id"] == 1

@pytest.mark.asyncio
async def test_supervisor_agent_loop_detection(sample_state):
    sample_state["session_context"]["revision_count"] = 10
    
    result = await supervisor_agent(sample_state)
    
    assert result["agent_interactions"][0]["next_agent"] == "summarizer"
    assert "Loop limit reached" in result["agent_interactions"][0]["answer"]
