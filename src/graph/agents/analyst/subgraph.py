from src.graph.utils.agents import with_logging
from typing import TypedDict, Optional, Annotated, List
import operator
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from src.graph.agents.analyst.prompts import INSTRUCTION_GENERATOR_PROMPT, BULL_PROMPT, BEAR_PROMPT, SYNTHESIS_PROMPT
from src.graph.utils.prompt import convert_state_to_prompt
from src.graph.state import AgentInteraction, SessionContext
from src.graph.utils.agents import get_next_interaction_id

class DebateState(TypedDict):
    research_data: str
    user_input: str
    session_context: SessionContext
    bull_instruction: Optional[str]
    bear_instruction: Optional[str]
    agent_interactions: Annotated[List[AgentInteraction], operator.add]
    bull_argument: Optional[str]
    bear_argument: Optional[str]
    final_report: Optional[str]
    confidence_score: int

class Instructions(BaseModel):
    bull_instruction: str = Field(description="Adversarial prompt for the Bull Analyst")
    bear_instruction: str = Field(description="Adversarial prompt for the Bear Analyst")

def generate_instructions(state: DebateState):
    """
    Debate Orchestrator: Analyzes research data to generate adversarial instructions for sub-agents.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(Instructions, method="function_calling")
    
    prompt = INSTRUCTION_GENERATOR_PROMPT.format(
        current_context=convert_state_to_prompt(state)
    )
    
    result = structured_llm.invoke([SystemMessage(content=prompt)])
    return {
        "bull_instruction": result.bull_instruction,
        "bear_instruction": result.bear_instruction,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "generator",
            "answer": f"Bull Instruction:\n{result.bull_instruction}\n\nBear Instruction:\n{result.bear_instruction}",
            "next_agent": "bull and bear"
        }]
    }

@with_logging
def bull_agent(state: DebateState):
    """
    Bull Analyst: Build the strongest possible 'Buy' case for the focus stocks.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    prompt = BULL_PROMPT.format(
        instruction=state["bull_instruction"],
        current_context=convert_state_to_prompt(state)
    )
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "bull_argument": response.content,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "bull",
            "answer": response.content,
            "next_agent": "synthesizer"
        }]
    }

@with_logging
def bear_agent(state: DebateState):
    """
    Bear Analyst: Build the strongest possible 'Sell' or 'Avoid' case for the focus stocks.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    prompt = BEAR_PROMPT.format(
        instruction=state["bear_instruction"],
        current_context=convert_state_to_prompt(state)
    )
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "bear_argument": response.content,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "bear",
            "answer": response.content,
            "next_agent": "synthesizer"
        }]
    }

class FinalSynthesis(BaseModel):
    report: str = Field(description="The full synthesized report in Markdown")
    confidence_score: int = Field(description="Overall confidence in the synthesis (0-100)")

def synthesizer(state: DebateState):
    """
    Moderator: Synthesizes a final, unbiased report based on the adversarial arguments.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(FinalSynthesis, method="function_calling")
    
    prompt = SYNTHESIS_PROMPT.format(
        bull_argument=state["bull_argument"],
        bear_argument=state["bear_argument"],
        current_context=convert_state_to_prompt(state)
    )
    
    result = structured_llm.invoke([SystemMessage(content=prompt)])
    return {
        "final_report": result.report,
        "confidence_score": result.confidence_score,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "synthesizer",
            "answer": f"Confidence Score: {result.confidence_score}/100\n\n{result.report}",
            "next_agent": "analyst (end)"
        }]
    }

def create_debate_graph():
    builder = StateGraph(DebateState)
    
    builder.add_node("generator", generate_instructions)
    builder.add_node("bull", bull_agent)
    builder.add_node("bear", bear_agent)
    builder.add_node("synthesizer", synthesizer)
    
    builder.add_edge(START, "generator")
    builder.add_edge("generator", "bull")
    builder.add_edge("generator", "bear")
    builder.add_edge(["bull", "bear"], "synthesizer")
    builder.add_edge("synthesizer", END)
    
    return builder.compile()
