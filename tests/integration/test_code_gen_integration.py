import pytest
from src.graph.graph import create_graph
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_code_gen_parallel_flow():
    # Test that Supervisor can trigger code_generator in parallel with other researchers
    query = "Analyze TSLA news and calculate its sector weight"
    
    # PATCH THE SYMBOLS AS THEY ARE IMPORTED IN src.graph.graph
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.fundamental_researcher", new_callable=AsyncMock) as mock_fund, \
         patch("src.graph.graph.sentiment_researcher", new_callable=AsyncMock) as mock_sent, \
         patch("src.graph.graph.macro_researcher", new_callable=AsyncMock) as mock_macro, \
         patch("src.graph.graph.narrative_researcher", new_callable=AsyncMock) as mock_narrative, \
         patch("src.graph.graph.generic_researcher", new_callable=AsyncMock) as mock_generic, \
         patch("src.graph.graph.code_generator_agent", new_callable=AsyncMock) as mock_code, \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.off_topic_agent", new_callable=AsyncMock) as mock_off, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        # 1. Supervisor triggers parallel
        mock_sup.return_value = {
            "agent_interactions": [{
                "agent": "supervisor", 
                "answer": "Routing", 
                "next_agent": "sentiment_researcher, code_generator"
            }]
        }
        
        mock_sent.return_value = {"agent_interactions": [{"agent": "sentiment_researcher", "answer": "SENTIMENT", "next_agent": "analyst"}]}
        mock_code.return_value = {"agent_interactions": [{"agent": "code_generator", "answer": "CALCULATION", "next_agent": "analyst"}]}
        mock_analyst.return_value = {"agent_interactions": [{"agent": "analyst", "answer": "REPORT", "next_agent": "summarizer"}]}
        mock_summ.return_value = {"agent_interactions": [{"agent": "summarizer", "answer": "SUMMARY", "next_agent": "end"}]}
        
        # CREATE GRAPH INSIDE PATCH
        graph = create_graph()
        initial_state = {
            "user_input": query,
            "agent_interactions": [],
            "session_context": {"revision_count": 0},
            "code_revision_count": 0,
            "user_context": {"portfolio": []}
        }
        
        result = await graph.ainvoke(initial_state)
        
        agents_called = [i["agent"] for i in result["agent_interactions"]]
        assert "code_generator" in agents_called
        assert "sentiment_researcher" in agents_called
        assert "analyst" in agents_called

@pytest.mark.asyncio
async def test_analyst_to_code_gen_loop():
    # Test the feedback loop analyst -> code_generator
    query = "Calculate complex math"
    
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.code_generator_agent", new_callable=AsyncMock) as mock_code, \
         patch("src.graph.graph.fundamental_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.sentiment_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.macro_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.narrative_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.generic_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.off_topic_agent", new_callable=AsyncMock), \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        mock_sup.return_value = {"agent_interactions": [{"agent": "supervisor", "answer": "Start", "next_agent": "code_generator"}]}
        
        # First time code gen runs
        mock_code.side_effect = [
            {"agent_interactions": [{"agent": "code_generator", "answer": "CALC 1", "next_agent": "analyst"}]},
            {"agent_interactions": [{"agent": "code_generator", "answer": "CALC 2", "next_agent": "analyst"}]}
        ]
        
        # Analyst requests correction first time, then proceeds
        mock_analyst.side_effect = [
            {"agent_interactions": [{"agent": "analyst", "answer": "FIX IT", "next_agent": "code_generator"}], "code_revision_count": 1},
            {"agent_interactions": [{"agent": "analyst", "answer": "OK NOW", "next_agent": "summarizer"}]}
        ]
        
        mock_summ.return_value = {"agent_interactions": [{"agent": "summarizer", "answer": "DONE", "next_agent": "end"}]}
        
        # CREATE GRAPH INSIDE PATCH
        graph = create_graph()
        initial_state = {
            "user_input": query,
            "agent_interactions": [],
            "session_context": {"revision_count": 0},
            "code_revision_count": 0,
            "user_context": {"portfolio": []}
        }
        
        result = await graph.ainvoke(initial_state)
        
        agents_called = [i["agent"] for i in result["agent_interactions"]]
        # supervisor, code_gen, analyst, code_gen, analyst, summarizer
        assert agents_called.count("code_generator") == 2
        assert agents_called.count("analyst") == 2
        assert "summarizer" in agents_called

@pytest.mark.asyncio
async def test_analyst_loop_limit():
    # Test that the loop breaks after 2 revisions
    query = "Loop forever"
    
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.code_generator_agent", new_callable=AsyncMock) as mock_code, \
         patch("src.graph.graph.fundamental_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.sentiment_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.macro_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.narrative_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.generic_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.off_topic_agent", new_callable=AsyncMock), \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        mock_sup.return_value = {"agent_interactions": [{"agent": "supervisor", "answer": "Start", "next_agent": "code_generator"}]}
        
        mock_code.return_value = {"agent_interactions": [{"agent": "code_generator", "answer": "CALC", "next_agent": "analyst"}]}
        
        # Analyst ALWAYS requests correction
        mock_analyst.return_value = {
            "agent_interactions": [{"agent": "analyst", "answer": "STILL WRONG", "next_agent": "code_generator"}],
            "code_revision_count": 1 # This will be added to state each time
        }
        
        mock_summ.return_value = {"agent_interactions": [{"agent": "summarizer", "answer": "FORCE END", "next_agent": "end"}]}
        
        # CREATE GRAPH INSIDE PATCH
        graph = create_graph()
        initial_state = {
            "user_input": query,
            "agent_interactions": [],
            "session_context": {"revision_count": 0},
            "code_revision_count": 0,
            "user_context": {"portfolio": []}
        }
        
        # We need a higher recursion limit for multiple loops
        result = await graph.ainvoke(initial_state, config={"recursion_limit": 20})
        
        agents_called = [i["agent"] for i in result["agent_interactions"]]
        # 1. supervisor -> code_gen -> analyst (count=1) -> code_gen -> analyst (count=2) -> summarizer
        assert agents_called.count("code_generator") == 2
        assert agents_called.count("analyst") == 2
        assert "summarizer" in agents_called

@pytest.mark.asyncio
async def test_analyst_loop_behavioral_success():
    # Test that the graph proceeds to summarizer if the Analyst is satisfied after 1 revision
    query = "Calculate math"
    
    with patch("src.graph.graph.supervisor_agent", new_callable=AsyncMock) as mock_sup, \
         patch("src.graph.graph.code_generator_agent", new_callable=AsyncMock) as mock_code, \
         patch("src.graph.graph.fundamental_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.sentiment_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.macro_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.narrative_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.generic_researcher", new_callable=AsyncMock), \
         patch("src.graph.graph.off_topic_agent", new_callable=AsyncMock), \
         patch("src.graph.graph.analyst_agent", new_callable=AsyncMock) as mock_analyst, \
         patch("src.graph.graph.summarizer_agent", new_callable=AsyncMock) as mock_summ:
        
        mock_sup.return_value = {"agent_interactions": [{"agent": "supervisor", "answer": "Start", "next_agent": "code_generator"}]}
        
        mock_code.return_value = {"agent_interactions": [{"agent": "code_generator", "answer": "CALC", "next_agent": "analyst"}]}
        
        # 1st call: Analyst requests revision
        # 2nd call: Analyst is satisfied
        mock_analyst.side_effect = [
            {"agent_interactions": [{"agent": "analyst", "answer": "FIX", "next_agent": "code_generator"}], "code_revision_count": 1},
            {"agent_interactions": [{"agent": "analyst", "answer": "OK", "next_agent": "summarizer"}]}
        ]
        
        mock_summ.return_value = {"agent_interactions": [{"agent": "summarizer", "answer": "DONE", "next_agent": "end"}]}
        
        graph = create_graph()
        initial_state = {
            "user_input": query,
            "agent_interactions": [],
            "session_context": {"revision_count": 0},
            "code_revision_count": 0,
            "user_context": {"portfolio": []}
        }
        
        result = await graph.ainvoke(initial_state)
        
        agents_called = [i["agent"] for i in result["agent_interactions"]]
        # supervisor, code_gen, analyst, code_gen, analyst, summarizer
        assert agents_called.count("code_generator") == 2
        assert agents_called.count("analyst") == 2
        assert "summarizer" in agents_called
        assert result["code_revision_count"] == 1
