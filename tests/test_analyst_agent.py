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
            "research_data": "Some data",
            "user_question": "Analyze AAPL",
        }
        
        result = analyst_agent(state)
        
        assert "analysis_report" in result
        assert "Portfolio Analysis" in result["analysis_report"]
        assert result["next_agent"] == "cache_maintenance"
        assert result["debate_output"]["confidence_score"] == 85
        
        # Verify the graph was invoked with correct input
        mock_graph.invoke.assert_called_once_with({
            "research_data": "Some data",
            "user_question": "Analyze AAPL"
        })
