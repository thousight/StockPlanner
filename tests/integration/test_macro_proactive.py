import pytest
from src.graph.graph import create_graph
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_macro_proactive_trigger():
    # A simple stock analysis query
    query = "Analyze TSLA"
    
    # We patch the agent functions AS THEY ARE IMPORTED in src.graph.graph
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.fundamental_researcher", new_callable=AsyncMock) as mock_fund, \
         patch("src.graph.graph.macro_researcher", new_callable=AsyncMock) as mock_macro, \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        # 1. Supervisor logic (must include fundamental and macro)
        mock_sup.return_value = {
            "agent_interactions": [{
                "agent": "supervisor", 
                "answer": "Routing", 
                "next_agent": "fundamental_researcher, macro_researcher"
            }]
        }
        
        # 2. Researchers logic
        mock_fund.return_value = {"agent_interactions": [{"agent": "fundamental_researcher", "answer": "TSLA SEC DATA", "next_agent": "analyst"}]}
        mock_macro.return_value = {"agent_interactions": [{"agent": "macro_researcher", "answer": "MACRO DATA (GDP, CPI)", "next_agent": "analyst"}]}
        
        # 3. Analyst logic
        mock_analyst.return_value = {"agent_interactions": [{"agent": "analyst", "answer": "FINAL REPORT WITH MACRO", "next_agent": "summarizer"}]}
        
        # 4. Summarizer logic
        mock_summ.return_value = {"agent_interactions": [{"agent": "summarizer", "answer": "SUMMARY", "next_agent": "end"}]}
        
        graph = create_graph()
        initial_state = {
            "user_input": query,
            "agent_interactions": [],
            "session_context": {"revision_count": 0}
        }
        
        result = await graph.ainvoke(initial_state)
        
        interactions = result["agent_interactions"]
        agents_called = [i["agent"] for i in interactions]
        
        assert "supervisor" in agents_called
        assert "fundamental_researcher" in agents_called
        assert "macro_researcher" in agents_called
        assert "analyst" in agents_called
        assert "summarizer" in agents_called
