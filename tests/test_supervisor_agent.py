import pytest
from unittest.mock import patch, MagicMock
from src.agents.supervisor.agent import supervisor_agent
from src.state import AgentState, AgentInteraction
from src.agents.supervisor.response import SupervisorResponse

@patch('src.agents.supervisor.agent.ChatOpenAI')
def test_supervisor_routes_using_llm(mock_llm_class):
    """
    Test that the supervisor correctly uses LLM to route to a specialized agent.
    """
    mock_structured = MagicMock()
    mock_llm_class.return_value.with_structured_output.return_value = mock_structured
    
    # Mock the LLM output: Supervisor now only returns the next_agent.
    mock_structured.invoke.return_value = SupervisorResponse(next_agent="research")
    
    state: AgentState = {
        "session_context": {
            "current_datetime": "2026-02-28",
            "user_agent": "test-agent",
            "messages": [],
            "revision_count": 0
        },
        "user_context": {
            "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}]
        },
        "user_input": "Analyze my portfolio",
        "agent_interactions": [],
        "output": ""
    }
    
    result = supervisor_agent(state)
    interactions = result.get("agent_interactions", [])
    assert interactions[-1]["next_agent"] == "research"
    assert "research" in interactions[-1]["answer"]
    assert interactions[-1]["agent"] == "supervisor"
    assert result["session_context"]["revision_count"] == 1

@patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'})
def test_supervisor_loop_detection():
    """
    Test that the supervisor forces a route to summarizer if revision_count exceeds limit.
    """
    state: AgentState = {
        "session_context": {
            "current_datetime": "2026-02-28",
            "user_agent": "test-agent",
            "messages": [],
            "revision_count": 6  # Above threshold of 5
        },
        "user_context": {
            "portfolio": []
        },
        "user_input": "Loop test",
        "agent_interactions": [],
        "output": ""
    }
    
    result = supervisor_agent(state)
    interactions = result.get("agent_interactions", [])
    assert interactions[-1]["next_agent"] == "summarizer"
    assert "Loop limit reached" in interactions[-1]["answer"]
    assert result["session_context"]["revision_count"] == 1
