"""
Unit tests for the analyst node.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.nodes.analyst.node import analyst_node, build_portfolio_data_prompt


class TestBuildPortfolioDataPrompt:
    """Tests for the build_portfolio_data_prompt function."""
    
    def test_build_prompt_single_holding(self):
        """Test building prompt for a single holding."""
        portfolio = [
            {"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}
        ]
        research_data = {
            "AAPL": {
                "current_price": 175.0,
                "info": {"pe_ratio": 25.0, "market_cap": 2800000000000},
                "news": [
                    {"title": "Apple News", "summary": "Apple released new iPhone"}
                ]
            }
        }
        
        result = build_portfolio_data_prompt(portfolio, research_data)
        
        assert "AAPL" in result
        assert "10.0 shares" in result or "10 shares" in result
        assert "$150.00" in result
        assert "$175.00" in result
        assert "PE=25.0" in result
        assert "Apple News" in result
    
    def test_build_prompt_no_news(self):
        """Test prompt when no news is available."""
        portfolio = [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}]
        research_data = {
            "AAPL": {
                "current_price": 175.0,
                "info": {},
                "news": []
            }
        }
        
        result = build_portfolio_data_prompt(portfolio, research_data)
        
        assert "No news available" in result
    
    def test_build_prompt_missing_data(self):
        """Test prompt when research data is missing for a symbol."""
        portfolio = [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}]
        research_data = {}  # Empty research data
        
        result = build_portfolio_data_prompt(portfolio, research_data)
        
        # Should still include the symbol but with default values
        assert "AAPL" in result
        assert "$0.00" in result  # Default current price
    
    def test_build_prompt_multiple_holdings(self):
        """Test prompt with multiple holdings."""
        portfolio = [
            {"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0},
            {"symbol": "MSFT", "quantity": 5.0, "avg_cost": 300.0},
        ]
        research_data = {
            "AAPL": {"current_price": 175.0, "info": {}, "news": []},
            "MSFT": {"current_price": 350.0, "info": {}, "news": []},
        }
        
        result = build_portfolio_data_prompt(portfolio, research_data)
        
        assert "--- AAPL ---" in result
        assert "--- MSFT ---" in result
    
    def test_build_prompt_limits_news_to_three(self):
        """Test that only 3 news items are included."""
        portfolio = [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}]
        research_data = {
            "AAPL": {
                "current_price": 175.0,
                "info": {},
                "news": [
                    {"title": "News 1", "summary": "Summary 1"},
                    {"title": "News 2", "summary": "Summary 2"},
                    {"title": "News 3", "summary": "Summary 3"},
                    {"title": "News 4", "summary": "Summary 4"},  # Should be excluded
                ]
            }
        }
        
        result = build_portfolio_data_prompt(portfolio, research_data)
        
        assert "News 1" in result
        assert "News 2" in result
        assert "News 3" in result
        assert "News 4" not in result
    
    def test_build_prompt_handles_none_info(self):
        """Test that None info is handled gracefully."""
        portfolio = [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}]
        research_data = {
            "AAPL": {
                "current_price": 175.0,
                "info": None,
                "news": []
            }
        }
        
        result = build_portfolio_data_prompt(portfolio, research_data)
        
        assert "PE=None" in result  # Should handle None gracefully


class TestAnalystNode:
    """Tests for the analyst_node function."""
    
    @patch('src.agents.nodes.analyst.node.ChatOpenAI')
    def test_analyst_node_returns_report(self, mock_llm_class):
        """Test that analyst_node returns an analysis report."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "# Portfolio Analysis\n\nBuy AAPL"
        mock_llm_class.return_value = mock_llm
        
        state = {
            "portfolio": [
                {"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}
            ],
            "research_data": {
                "macro_economic_news": [
                    {"title": "Market Update", "summary": "Markets are stable"}
                ],
                "AAPL": {
                    "current_price": 175.0,
                    "info": {"pe_ratio": 25},
                    "news": []
                }
            }
        }
        
        result = analyst_node(state)
        
        assert "analysis_report" in result
        assert "Portfolio Analysis" in result["analysis_report"]
    
    @patch('src.agents.nodes.analyst.node.ChatOpenAI')
    def test_analyst_node_handles_llm_error(self, mock_llm_class):
        """Test that analyst_node handles LLM errors gracefully."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_llm_class.return_value = mock_llm
        
        state = {
            "portfolio": [],
            "research_data": {"macro_economic_news": []}
        }
        
        result = analyst_node(state)
        
        assert "analysis_report" in result
        assert "Error running analysis" in result["analysis_report"]
    
    @patch('src.agents.nodes.analyst.node.ChatOpenAI')
    def test_analyst_node_constructs_correct_messages(self, mock_llm_class):
        """Test that analyst_node sends correct message structure to LLM."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "Analysis"
        mock_llm_class.return_value = mock_llm
        
        state = {
            "portfolio": [{"symbol": "AAPL", "quantity": 10.0, "avg_cost": 150.0}],
            "research_data": {
                "macro_economic_news": [{"title": "News", "summary": "Summary"}],
                "AAPL": {"current_price": 175.0, "info": {}, "news": []}
            }
        }
        
        analyst_node(state)
        
        # Verify invoke was called with messages list
        call_args = mock_llm.invoke.call_args[0][0]
        assert len(call_args) == 2  # SystemMessage and HumanMessage
        assert "senior financial investment analyst" in call_args[0].content
