import pytest
from unittest.mock import AsyncMock, patch
from src.graph.agents.research.narrative import narrative_researcher
from src.graph.agents.research.research_plan import ResearchPlan
from src.graph.utils.tool_call import ToolCall

@pytest.mark.asyncio
async def test_narrative_researcher_orchestration():
    state = {"user_input": "Growth of Gold", "agent_interactions": []}
    
    # Mock a plan that uses multiple atomic tools
    mock_plan = ResearchPlan(
        steps=[
            ToolCall(tool_name="get_indices_performance", tool_params={}),
            ToolCall(tool_name="get_historical_narrative", tool_params={"subject": "Gold"}),
            ToolCall(tool_name="web_search", tool_params={"queries": ["Gold growth narrative 2026"]}),
            ToolCall(tool_name="synthesize_growth_narrative", tool_params={"subject": "Gold", "research_context": "..."})
        ], 
        next_agent="analyst"
    )
    
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct, \
         patch("src.graph.agents.research.narrative.execute_tool", new_callable=AsyncMock) as mock_exec:
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_plan
        mock_struct.return_value = mock_chain
        
        # Mock execute_tool to return string markers for each tool
        mock_exec.side_effect = [
            "Indices: SPY +1%",
            "History: Was bullish",
            "News: Gold is rising",
            "## Growth Narrative: Gold\nFinal Synthesis"
        ]
        
        result = await narrative_researcher(state)
        
        assert result["agent_interactions"][0]["agent"] == "narrative_researcher"
        # The answer should contain the combined output of all tools
        assert "Final Synthesis" in result["agent_interactions"][0]["answer"]
        assert "Indices: SPY" in result["agent_interactions"][0]["answer"]
        assert "History: Was bullish" in result["agent_interactions"][0]["answer"]
        
        # Verify execute_tool was called for each step in the plan
        assert mock_exec.call_count == 4
