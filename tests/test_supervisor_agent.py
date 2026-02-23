import pytest
from unittest.mock import patch, MagicMock
from src.agents.supervisor.agent import supervisor_agent
from src.state import AgentState
from src.agents.supervisor.high_level_plan import HighLevelPlan, PlanStep

@patch('src.agents.supervisor.agent.ChatOpenAI')
def test_supervisor_routes_using_llm(mock_llm_class):
    """
    Test that the supervisor correctly uses LLM to generate a HighLevelPlan and route.
    """
    mock_structured = MagicMock()
    mock_llm_class.return_value.with_structured_output.return_value = mock_structured
    
    # Mock the LLM output
    mock_structured.invoke.return_value = HighLevelPlan(
        steps=[
            PlanStep(id=1, description="Research AAPL"),
            PlanStep(id=2, description="Analyze data")
        ],
        next_agent="research",
        next_question="Perform stock research on AAPL",
        step_id=1
    )
    
    state: AgentState = {
        "messages": [],
        "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}],
        "user_input": "Analyze my portfolio",
        "revision_count": 0
    }
    
    result = supervisor_agent(state)
    interactions = result.get("agent_interactions", [])
    assert interactions[-1]["next_agent"] == "research"
    assert interactions[-1]["question"] == "Analyze my portfolio"
    assert interactions[-1]["next_question"] == "Perform stock research on AAPL"
    assert interactions[-1]["id"] == 1
    assert interactions[-1]["step_id"] == 1
    assert len(result["high_level_plan"]) == 2
    assert isinstance(result["high_level_plan"][0], dict)
    assert result["high_level_plan"][0]["id"] == 1

@patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'})
def test_supervisor_loop_detection():
    """
    Test that the supervisor forces a route to cache_maintenance if revision_count exceeds limit.
    """
    state: AgentState = {
        "messages": [],
        "portfolio": [],
        "user_input": "Loop test",
        "revision_count": 6  # Above threshold of 5
    }
    
    result = supervisor_agent(state)
    interactions = result.get("agent_interactions", [])
    assert interactions[-1]["next_agent"] == "summarizer"
