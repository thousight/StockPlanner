import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.graph.agents.analyst.agent import analyst_agent
from src.graph.agents.analyst.subgraph import (
    generate_instructions, 
    bull_agent, 
    bear_agent, 
    synthesizer,
    DebateState,
    Instructions,
    FinalSynthesis
)
from src.graph.state import AgentState

@pytest.fixture
def sample_state() -> AgentState:
    return {
        "session_context": {"messages": []},
        "user_context": {},
        "user_input": "Analyze AAPL",
        "agent_interactions": [
            {"id": 1, "agent": "research", "answer": "Apple is growing", "next_agent": "analyst"}
        ],
        "output": ""
    }

@pytest.mark.asyncio
async def test_analyst_agent_safety_approve(sample_state):
    # Mock debate graph result
    mock_debate_result = {
        "final_report": "High risk trade: BUY AAPL",
        "bull_argument": "Bullish",
        "bear_argument": "Bearish",
        "confidence_score": 80,
        "agent_interactions": sample_state["agent_interactions"] + [{"id": 2, "agent": "synthesizer"}]
    }
    
    with patch("src.graph.agents.analyst.agent.create_debate_graph") as mock_graph_creator:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_debate_result
        mock_graph_creator.return_value = mock_graph
        
        # Mock safety interrupt to 'approve'
        with patch("src.graph.agents.analyst.agent.interrupt") as mock_interrupt:
            mock_interrupt.return_value = "approve"
            
            result = await analyst_agent(sample_state, config={})
            
            assert "agent_interactions" in result
            last_itr = result["agent_interactions"][-1]
            assert last_itr["agent"] == "analyst"
            assert "BUY AAPL" in last_itr["answer"]
            assert last_itr["next_agent"] == "summarizer"

@pytest.mark.asyncio
async def test_analyst_agent_safety_cancel(sample_state):
    mock_debate_result = {
        "final_report": "High risk trade: SELL AAPL",
        "agent_interactions": sample_state["agent_interactions"] + [{"id": 2, "agent": "synthesizer"}]
    }
    
    with patch("src.graph.agents.analyst.agent.create_debate_graph") as mock_graph_creator:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_debate_result
        mock_graph_creator.return_value = mock_graph
        
        with patch("src.graph.agents.analyst.agent.interrupt") as mock_interrupt:
            mock_interrupt.return_value = "cancel that"
            
            result = await analyst_agent(sample_state, config={})
            
            last_itr = result["agent_interactions"][-1]
            assert "cancelled by the user" in last_itr["answer"]
            assert last_itr["next_agent"] == "summarizer"

def test_generate_instructions():
    state = {"research_data": "Data", "agent_interactions": []}
    mock_instr = Instructions(bull_instruction="Bull", bear_instruction="Bear")
    
    with patch("src.graph.agents.analyst.subgraph.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = mock_instr
        mock_llm.with_structured_output.return_value = mock_structured
        
        result = generate_instructions(state)
        assert result["bull_instruction"] == "Bull"
        assert result["bear_instruction"] == "Bear"

@pytest.mark.asyncio
async def test_bull_agent():
    state = {"bull_instruction": "Be Bullish", "agent_interactions": []}
    mock_msg = MagicMock(content="I love Apple")
    
    with patch("src.graph.agents.analyst.subgraph.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_llm.invoke.return_value = mock_msg
        
        # bull_agent is decorated with @with_logging, but it is sync in the file?
        # Let's check subgraph.py again. Ah, bull_agent and bear_agent are decorated but NOT async def?
        # Wait, I'll check the file again.
        result = bull_agent(state)
        assert result["bull_argument"] == "I love Apple"

def test_synthesizer():
    state = {"bull_argument": "Bull", "bear_argument": "Bear", "agent_interactions": []}
    mock_final = FinalSynthesis(report="Balanced", confidence_score=90)
    
    with patch("src.graph.agents.analyst.subgraph.ChatOpenAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = mock_final
        mock_llm.with_structured_output.return_value = mock_structured
        
        result = synthesizer(state)
        assert result["final_report"] == "Balanced"
        assert result["confidence_score"] == 90
