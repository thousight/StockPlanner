import pytest
from src.graph.graph import create_graph
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_complex_modular_flow_parallel():
    # Test a query that should trigger parallel research
    query = "Analyze AAPL fundamentals and sentiment"
    
    # We patch the agent functions AS THEY ARE IMPORTED in src.graph.graph
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.fundamental_researcher", new_callable=AsyncMock) as mock_fund, \
         patch("src.graph.graph.sentiment_researcher", new_callable=AsyncMock) as mock_sent, \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        # 1. Supervisor logic (Parallel)
        mock_sup.return_value = {
            "agent_interactions": [{
                "agent": "supervisor", 
                "answer": "Routing", 
                "next_agent": "fundamental_researcher, sentiment_researcher"
            }]
        }
        
        # 2. Researchers logic
        mock_fund.return_value = {"agent_interactions": [{"agent": "fundamental_researcher", "answer": "SEC DATA", "next_agent": "analyst"}]}
        mock_sent.return_value = {"agent_interactions": [{"agent": "sentiment_researcher", "answer": "SOCIAL DATA", "next_agent": "analyst"}]}
        
        # 3. Analyst logic
        mock_analyst.return_value = {"agent_interactions": [{"agent": "analyst", "answer": "FINAL REPORT", "next_agent": "summarizer"}]}
        
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
        assert "sentiment_researcher" in agents_called
        assert "analyst" in agents_called
        assert "summarizer" in agents_called
