"""
Unit tests for the analyst agent.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.analyst.agent import analyst_agent
from src.state import AgentState

class TestAnalystAgent:
    """Tests for the analyst_agent function."""
    
    @patch('src.agents.analyst.agent.create_debate_graph')
    def test_analyst_agent_returns_report(self, mock_create_debate_graph):
        """Test that analyst_agent returns an analysis report via the debate graph."""
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "bull_argument": "Bull case",
            "bear_argument": "Bear case",
            "confidence_score": 85,
            "final_report": "# Portfolio Analysis\n\nBuy AAPL",
            "agent_interactions": [
                {
                    "id": 1,
                    "agent": "research",
                    "answer": "Some data",
                    "next_agent": "analyst",
                },
                {
                    "id": 2,
                    "agent": "generator",
                    "answer": "Instructions",
                    "next_agent": "bull and bear"
                }
            ]
        }
        mock_create_debate_graph.return_value = mock_graph
        
        state: AgentState = {
            "session_context": {
                "current_datetime": "2026-02-28",
                "user_agent": "test",
                "messages": [],
                "revision_count": 0
            },
            "user_context": {
                "portfolio": [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}]
            },
            "user_input": "Analyze AAPL",
            "agent_interactions": [{
                "id": 1,
                "agent": "research",
                "answer": "Some data",
                "next_agent": "analyst",
            }],
            "output": ""
        }
        
        config = {"configurable": {"thread_id": "test"}}
        
        result = analyst_agent(state, config)
        
        # Check interactions
        interactions = result.get("agent_interactions", [])
        analyst_int = next((i for i in interactions if i["agent"] == "analyst"), None)
        assert analyst_int is not None
        assert analyst_int["debate_output"]["confidence_score"] == 85
        assert analyst_int["answer"] == "# Portfolio Analysis\n\nBuy AAPL"
        assert analyst_int["next_agent"] == "summarizer"
        assert analyst_int["id"] == 3  # 1 initial + 1 from generator (id 2) + 1 for analyst
        
        # Verify the graph was invoked with correct input
        mock_graph.invoke.assert_called_once()
        call_args = mock_graph.invoke.call_args[0][0]
        assert call_args["research_data"] == "Some data"
        assert call_args["user_input"] == "Analyze AAPL"
