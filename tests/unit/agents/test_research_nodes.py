import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.agents.research.fundamental import fundamental_researcher
from src.graph.agents.research.sentiment import sentiment_researcher
from src.graph.agents.research.macro import macro_researcher
from src.graph.agents.research.generic import generic_researcher
from src.graph.agents.research.research_plan import ResearchPlan
from src.graph.utils.tool_call import ToolCall

@pytest.mark.asyncio
async def test_fundamental_researcher():
    state = {"user_input": "AAPL 10-K", "agent_interactions": []}
    mock_plan = ResearchPlan(
        steps=[ToolCall(tool_name="get_stock_financials", tool_params={"symbol": "AAPL"})], 
        next_agent="analyst"
    )
    
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct, \
         patch("src.graph.agents.research.utils.execute_tool", new_callable=AsyncMock) as mock_exec:
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_plan
        mock_struct.return_value = mock_chain
        mock_exec.return_value = "Financial Data"
        
        result = await fundamental_researcher(state)
        assert result["agent_interactions"][0]["agent"] == "fundamental_researcher"
        assert "Financial Data" in result["agent_interactions"][0]["answer"]
@pytest.mark.asyncio
async def test_sentiment_researcher():
    state = {"user_input": "NVDA sentiment", "agent_interactions": []}
    mock_plan = ResearchPlan(
        steps=[ToolCall(tool_name="get_market_sentiment", tool_params={"ticker": "NVDA"})], 
        next_agent="analyst"
    )

    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct, \
         patch("src.graph.agents.research.sentiment.execute_tool", new_callable=AsyncMock) as mock_exec:

        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_plan
        mock_struct.return_value = mock_chain
        mock_exec.return_value = "Sentiment Pulse"

        result = await sentiment_researcher(state)
        assert result["agent_interactions"][0]["agent"] == "sentiment_researcher"
        assert "Sentiment Pulse" in result["agent_interactions"][0]["answer"]

@pytest.mark.asyncio
async def test_macro_researcher():
    state = {"user_input": "Interest rates", "agent_interactions": []}
    mock_plan = ResearchPlan(
        steps=[ToolCall(tool_name="get_macro_economic_news", tool_params={})], 
        next_agent="analyst"
    )
    
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct, \
         patch("src.graph.agents.research.utils.execute_tool", new_callable=AsyncMock) as mock_exec:
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_plan
        mock_struct.return_value = mock_chain
        mock_exec.return_value = "Macro Context"
        
        result = await macro_researcher(state)
        assert result["agent_interactions"][0]["agent"] == "macro_researcher"
        assert "Macro Context" in result["agent_interactions"][0]["answer"]

@pytest.mark.asyncio
async def test_generic_researcher():
    state = {"user_input": "AI chip competitors", "agent_interactions": []}
    mock_plan = ResearchPlan(
        steps=[ToolCall(tool_name="web_search", tool_params={"queries": ["AI chip competitors"]})], 
        next_agent="analyst"
    )
    
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct, \
         patch("src.graph.agents.research.utils.execute_tool", new_callable=AsyncMock) as mock_exec:
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_plan
        mock_struct.return_value = mock_chain
        mock_exec.return_value = "General Research Data"
        
        result = await generic_researcher(state)
        assert result["agent_interactions"][0]["agent"] == "generic_researcher"
        assert "General Research Data" in result["agent_interactions"][0]["answer"]
