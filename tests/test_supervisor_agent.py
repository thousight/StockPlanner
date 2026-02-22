import pytest
from unittest.mock import patch, MagicMock
from src.agents.supervisor.agent import supervisor_agent
from src.state import AgentState
from src.agents.supervisor.high_level_plan import HighLevelPlan

@patch('src.agents.supervisor.agent.ChatOpenAI')
def test_supervisor_routes_using_llm(mock_llm_class):
    """
    Test that the supervisor correctly uses LLM to generate a HighLevelPlan and route.
    """
    mock_structured = MagicMock()
    mock_llm_class.return_value.with_structured_output.return_value = mock_structured
    
    # Mock the LLM output
    mock_structured.invoke.return_value = HighLevelPlan(
        steps=["Research AAPL", "Analyze data"],
        next_agent="research"
    )
    
    state: AgentState = {
        "messages": [],
        "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}],
        "research_data": "",
        "analysis_report": "",
        "next_agent": "",
        "revision_count": 0
    }
    
    result = supervisor_agent(state)
    assert result["next_agent"] == "research"
    assert len(result["high_level_plan"]) == 2
    assert result["revision_count"] == 1

@patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'})
def test_supervisor_loop_detection():
    """
    Test that the supervisor forces a route to cache_maintenance if revision_count exceeds limit.
    """
    state: AgentState = {
        "messages": [],
        "portfolio": [],
        "research_data": "",
        "analysis_report": "",
        "next_agent": "",
        "revision_count": 6  # Above threshold of 5
    }
    
    result = supervisor_agent(state)
    assert result["next_agent"] == "cache_maintenance"
