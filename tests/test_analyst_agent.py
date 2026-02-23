"""
Unit tests for the analyst agent.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.analyst.agent import analyst_agent

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
            "final_report": "# Portfolio Analysis\n\nBuy AAPL"
        }
        mock_create_debate_graph.return_value = mock_graph
        
        state = {
            "portfolio": [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}],
            "user_input": "Analyze AAPL",
            "agent_interactions": [{
                "id": 1,
                "step_id": 1,
                "agent": "research",
                "question": "Research AAPL",
                "answer": "Some data",
                "next_agent": "analyst",
                "next_question": "Analyze the findings for AAPL"
            }]
        }
        
        config = {"configurable": {"thread_id": "test"}}
        
        result = analyst_agent(state, config)
        
        # Check interactions
        analyst_int = next((i for i in result["agent_interactions"] if i["agent"] == "analyst"), None)
        assert analyst_int is not None
        assert analyst_int["debate_output"]["confidence_score"] == 85
        assert analyst_int["answer"] == "# Portfolio Analysis\n\nBuy AAPL"
        
        assert analyst_int["next_agent"] == "summarizer"
        assert analyst_int["question"] == "Analyze the findings for AAPL"
        assert "Summarize" in analyst_int["next_question"]
        assert analyst_int["id"] == 2
        assert analyst_int["step_id"] == 1
        assert "output" not in result
        
        # Verify the graph was invoked with correct input
        mock_graph.invoke.assert_called_once_with({
            "research_data": "Some data",
            "user_input": "Analyze AAPL"
        }, config=config)
