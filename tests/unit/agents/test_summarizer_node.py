import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.graph.agents.summarizer.agent import summarizer_agent, SummarizerOutput
from src.graph.state import AgentState

@pytest.fixture
def sample_state() -> AgentState:
    return {
        "session_context": {"messages": []},
        "user_context": {},
        "user_input": "What do you think of AAPL?",
        "agent_interactions": [
            {"id": 1, "agent": "research", "answer": "Data"},
            {"id": 2, "agent": "analyst", "answer": "Analysis"}
        ],
        "output": ""
    }

@pytest.mark.asyncio
async def test_summarizer_agent_success(sample_state):
    mock_output = SummarizerOutput(
        final_answer="Final Synthesis",
        title="Apple Analysis",
        category="STOCK",
        topic="AAPL",
        tags=["#growth", "#tech"]
    )
    
    with patch("src.graph.agents.summarizer.agent.get_llm") as mock_llm_func:
        mock_llm = MagicMock()
        mock_llm_func.return_value = mock_llm
        
        mock_structured = AsyncMock()
        mock_structured.ainvoke.return_value = mock_output
        mock_llm.with_structured_output.return_value = mock_structured
        
        result = await summarizer_agent(sample_state)
        
        assert result["output"] == "Final Synthesis"
        assert result["agent_interactions"][0]["agent"] == "summarizer"
