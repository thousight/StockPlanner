import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from decimal import Decimal
from src.graph.agents.research.agent import research_agent, execute_tool, TOOLS_LIST
from src.graph.agents.research.research_plan import ResearchPlan
from src.graph.utils.tool_call import ToolCall
from src.graph.state import AgentState

@pytest.fixture
def sample_state() -> AgentState:
    return {
        "session_context": {
            "user_agent": "TestAgent/1.0",
            "messages": [],
            "revision_count": 0
        },
        "user_context": {},
        "user_input": "Analyze AAPL",
        "agent_interactions": [],
        "output": ""
    }

@pytest.mark.asyncio
async def test_research_agent_success(sample_state):
    # 1. Mock the structured LLM response
    mock_plan = ResearchPlan(
        next_agent="analyst",
        steps=[
            ToolCall(tool_name="get_stock_financials", tool_params={"symbol": "AAPL"}),
            ToolCall(tool_name="get_stock_news", tool_params={"symbol": "AAPL"})
        ]
    )
    
    # 2. Setup mocks
    with patch("src.graph.agents.research.agent.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        
        mock_structured = AsyncMock()
        mock_structured.ainvoke.return_value = mock_plan
        mock_llm.with_structured_output.return_value = mock_structured
        
        # Mock execute_tool to avoid actual API calls
        with patch("src.graph.agents.research.agent.execute_tool", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [
                "Financials: Good\n",
                "News: Bullish\n"
            ]
            
            result = await research_agent(sample_state)
            
            # 3. Assertions
            assert "agent_interactions" in result
            interaction = result["agent_interactions"][0]
            assert interaction["agent"] == "research"
            assert "Financials: Good" in interaction["answer"]
            assert "News: Bullish" in interaction["answer"]
            assert interaction["next_agent"] == "analyst"
            assert interaction["id"] == 1

@pytest.mark.asyncio
async def test_execute_tool_web_search_param_fix():
    # Test that execute_tool fixes 'query' or 'q' for web_search
    step = ToolCall(tool_name="web_search", tool_params={"query": "AAPL news"})
    
    # Use real async function instead of AsyncMock for parameter verification
    async def mock_web_search(queries=None, user_agent=None):
        return f"Search for {queries} with {user_agent}"
    mock_web_search.__name__ = "web_search"
    
    # Let's find web_search in TOOLS_LIST and replace it for this test
    for i, tool in enumerate(TOOLS_LIST):
        if tool.__name__ == "web_search":
            old_tool = TOOLS_LIST[i]
            TOOLS_LIST[i] = mock_web_search
            try:
                result = await execute_tool(step, user_agent="TestUA")
                assert "Search for ['AAPL news'] with TestUA" in result
            finally:
                TOOLS_LIST[i] = old_tool

@pytest.mark.asyncio
async def test_execute_tool_not_found():
    step = ToolCall(tool_name="non_existent_tool", tool_params={})
    result = await execute_tool(step)
    assert "Tool non_existent_tool not found" in result

@pytest.mark.asyncio
async def test_execute_tool_exception():
    step = ToolCall(tool_name="get_stock_financials", tool_params={"symbol": "AAPL"})
    
    async def mock_fail(*args, **kwargs):
        raise Exception("API Error")
    mock_fail.__name__ = "get_stock_financials"

    for i, tool in enumerate(TOOLS_LIST):
        if tool.__name__ == "get_stock_financials":
            old_tool = TOOLS_LIST[i]
            TOOLS_LIST[i] = mock_fail
            try:
                result = await execute_tool(step)
                assert "Error executing tool get_stock_financials: API Error" in result
            finally:
                TOOLS_LIST[i] = old_tool
