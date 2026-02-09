"""
Unit tests for the research node.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.nodes.research.node import research_node, fetch_symbol_data


class TestResearchNode:
    """Tests for the research_node function."""
    
    @patch('src.agents.nodes.research.node.get_macro_economic_news')
    @patch('src.agents.nodes.research.node.resolve_symbol')
    def test_research_node_returns_research_data(self, mock_resolve, mock_macro):
        """Test that research_node returns properly structured data."""
        # Setup mocks
        mock_macro.return_value = [
            {"title": "Market Update", "summary": "Stocks are up"}
        ]
        mock_resolve.return_value = {
            "current_price": 150.0,
            "news": [{"title": "AAPL News", "summary": "Apple released new product"}],
            "info": {"pe_ratio": 25.0}
        }
        
        state = {
            "portfolio": [
                {"symbol": "AAPL", "quantity": 10, "avg_cost": 140.0}
            ]
        }
        
        result = research_node(state)
        
        assert "research_data" in result
        assert "macro_economic_news" in result["research_data"]
        assert "AAPL" in result["research_data"]
    
    @patch('src.agents.nodes.research.node.get_macro_economic_news')
    @patch('src.agents.nodes.research.node.resolve_symbol')
    def test_research_node_handles_multiple_symbols(self, mock_resolve, mock_macro):
        """Test research_node with multiple portfolio holdings."""
        mock_macro.return_value = []
        mock_resolve.side_effect = [
            {"current_price": 150.0, "news": [], "info": {}},
            {"current_price": 300.0, "news": [], "info": {}},
        ]
        
        state = {
            "portfolio": [
                {"symbol": "AAPL", "quantity": 10, "avg_cost": 140.0},
                {"symbol": "MSFT", "quantity": 5, "avg_cost": 280.0},
            ]
        }
        
        result = research_node(state)
        
        assert "AAPL" in result["research_data"]
        assert "MSFT" in result["research_data"]
    
    @patch('src.agents.nodes.research.node.get_macro_economic_news')
    @patch('src.agents.nodes.research.node.resolve_symbol')
    def test_research_node_empty_portfolio(self, mock_resolve, mock_macro):
        """Test research_node with empty portfolio."""
        mock_macro.return_value = [{"title": "News", "summary": "Summary"}]
        
        state = {"portfolio": []}
        
        result = research_node(state)
        
        assert "research_data" in result
        assert "macro_economic_news" in result["research_data"]
        mock_resolve.assert_not_called()


class TestFetchSymbolData:
    """Tests for the fetch_symbol_data helper function."""
    
    @patch('src.agents.nodes.research.node.resolve_symbol')
    def test_fetch_symbol_data_returns_tuple(self, mock_resolve):
        """Test that fetch_symbol_data returns (symbol, data) tuple."""
        mock_resolve.return_value = {"current_price": 100.0}
        
        holding = {"symbol": "AAPL", "quantity": 10, "avg_cost": 90.0}
        result = fetch_symbol_data(holding)
        
        assert isinstance(result, tuple)
        assert result[0] == "AAPL"
        assert result[1] == {"current_price": 100.0}
    
    @patch('src.agents.nodes.research.node.resolve_symbol')
    def test_fetch_symbol_data_calls_resolve_symbol(self, mock_resolve):
        """Test that fetch_symbol_data calls resolve_symbol with correct symbol."""
        mock_resolve.return_value = {}
        
        holding = {"symbol": "NVDA", "quantity": 5, "avg_cost": 200.0}
        fetch_symbol_data(holding)
        
        mock_resolve.assert_called_once_with("NVDA")
