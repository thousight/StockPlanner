import pytest
from src.agents.nodes.supervisor.node import supervisor_node
from src.agents.state import AgentState

def test_supervisor_routes_to_financials_when_no_data():
    """
    Test that the supervisor correctly routes to 'financials' worker when research_data is missing.
    """
    state: AgentState = {
        "messages": [],
        "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}],
        "research_data": {},
        "analysis_report": "",
        "next_node": ""
    }
    
    result = supervisor_node(state)
    assert result["next_node"] == "financials"

def test_supervisor_routes_to_analyst_when_data_exists():
    """
    Test that the supervisor routes to 'analyst' node when research_data is present but report is missing.
    """
    state: AgentState = {
        "messages": [],
        "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}],
        "research_data": {
            "AAPL": {"current_price": 180.0, "info": {"pe": 30}, "news": [{"title": "News"}]},
            "macro_economic_news": [{"title": "Macro News", "summary": "Steady"}]
        },
        "analysis_report": "",
        "next_node": ""
    }
    
    result = supervisor_node(state)
    assert result["next_node"] == "analyst"

def test_supervisor_routes_to_end_when_report_complete():
    """
    Test that the supervisor routes to 'end' when analysis_report is already complete.
    """
    state: AgentState = {
        "messages": [],
        "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}],
        "research_data": {
            "AAPL": {"current_price": 180.0, "info": {"pe": 30}, "news": [{"title": "News"}]},
            "macro_economic_news": [{"title": "Macro"}]
        },
        "analysis_report": "This is a completed analysis report.",
        "next_node": ""
    }
    
    result = supervisor_node(state)
    assert result["next_node"] == "end"
