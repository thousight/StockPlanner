import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.graph.agents.analyst.agent import analyst_agent

@pytest.fixture
def mock_state():
    return {
        "user_input": "Test Query",
        "user_context": {"portfolio": []},
        "agent_interactions": [
            {
                "agent": "code_generator",
                "answer": "<calculation_result>Result: 42</calculation_result>",
                "next_agent": "analyst"
            }
        ],
        "session_context": {"revision_count": 0}
    }

@pytest.mark.asyncio
async def test_analyst_collects_code_gen_data(mock_state):
    # Mock the debate subgraph to avoid real LLM calls
    mock_debate_results = {
        "final_report": "Analysis Report\nFOLLOW_UP: None",
        "agent_interactions": mock_state["agent_interactions"] + [{"agent": "debate_orchestrator", "answer": "Debate logic"}]
    }
    
    with patch("src.graph.agents.analyst.agent.create_debate_graph") as mock_create_graph:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_debate_results
        mock_create_graph.return_value = mock_graph
        
        result = await analyst_agent(mock_state, config=MagicMock())
        
        # Verify research_data passed to subgraph included code_generator
        # We need to check call_args of ainvoke
        args, kwargs = mock_graph.ainvoke.call_args
        passed_input = args[0]
        assert "Data from code_generator" in passed_input["research_data"]
        assert "<calculation_result>Result: 42" in passed_input["research_data"]

@pytest.mark.asyncio
async def test_analyst_requests_code_gen_correction(mock_state):
    mock_debate_results = {
        "final_report": "Numbers look weird.\nFOLLOW_UP: code_generator | The volatility is too high, please fix.",
        "agent_interactions": mock_state["agent_interactions"] + [{"agent": "debate_orchestrator", "answer": "Fix needed"}]
    }
    
    with patch("src.graph.agents.analyst.agent.create_debate_graph") as mock_create_graph:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_debate_results
        mock_create_graph.return_value = mock_graph
        
        result = await analyst_agent(mock_state, config=MagicMock())
        
        # Last interaction should be from analyst
        interactions = result["agent_interactions"]
        analyst_interaction = interactions[-1]
        assert analyst_interaction["agent"] == "analyst"
        assert analyst_interaction["next_agent"] == "code_generator"
