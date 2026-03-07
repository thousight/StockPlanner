import pytest
from unittest.mock import AsyncMock, patch
from src.graph.graph import create_graph

@pytest.mark.asyncio
async def test_narrative_researcher_graph_integration():
    """
    Graph integration test for NarrativeResearcher.
    Verifies that the graph can route to and from the narrative researcher without live calls.
    """
    query = "What is the broad market growth narrative today?"
    
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.narrative_researcher", new_callable=AsyncMock) as mock_narrative, \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        # 1. Supervisor routes to narrative
        mock_sup.return_value = {
            "agent_interactions": [{
                "agent": "supervisor", 
                "answer": "Routing to narrative", 
                "next_agent": "narrative_researcher"
            }]
        }
        
        # 2. Narrative researcher returns data
        mock_narrative.return_value = {
            "agent_interactions": [{
                "agent": "narrative_researcher", 
                "answer": "Market Narrative: Bullish", 
                "next_agent": "analyst"
            }]
        }
        
        # 3. Analyst processes
        mock_analyst.return_value = {
            "agent_interactions": [{
                "agent": "analyst", 
                "answer": "Analysis complete", 
                "next_agent": "summarizer"
            }]
        }
        
        # 4. Summarizer ends
        mock_summ.return_value = {
            "agent_interactions": [{
                "agent": "summarizer", 
                "answer": "Final Summary", 
                "next_agent": "end"
            }]
        }
        
        graph = create_graph()
        initial_state = {
            "user_input": query,
            "agent_interactions": [],
            "session_context": {"revision_count": 0},
            "user_context": {"portfolio": []}
        }
        
        result = await graph.ainvoke(initial_state)
        
        agents_called = [i["agent"] for i in result["agent_interactions"]]
        assert "supervisor" in agents_called
        assert "narrative_researcher" in agents_called
        assert "analyst" in agents_called
        assert "summarizer" in agents_called
