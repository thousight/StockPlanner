import uuid
from typing import List, Optional

from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.graph.agents.summarizer.prompts import SUMMARIZER_SYSTEM_PROMPT
from src.graph.state import AgentState
from src.graph.utils.agents import create_interaction, get_llm, with_logging
from src.graph.utils.prompt import convert_state_to_prompt

class SummarizerOutput(BaseModel):
    """
    Structured output from the Summarizer Agent.
    """
    final_answer: str = Field(description="The synthesized final response to the user in Markdown format. Must be in the user's language.")
    title: str = Field(description="A concise and descriptive title for the report.")
    category: str = Field(description="The primary category of the report: STOCK, REAL_ESTATE, MACRO, FUND, or GENERAL.")
    topic: str = Field(description="The specific topic of the report (e.g., 'NVDA', 'Gold Market').")
    tags: List[str] = Field(description="2-3 hashtags summarizing the content (e.g., #growth, #volatility).")

@with_logging
async def summarizer_agent(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Summarizer Agent: Reviews all agent interactions and synthesizes a final answer.
    """
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(SummarizerOutput)
        
    system_msg = SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state)
    ))
        
    response = await structured_llm.ainvoke([system_msg])
    final_content = response.final_answer
        
    return {
        "output": final_content,
        "session_context": {
            "messages": [AIMessage(content=final_content, id=str(uuid.uuid4()))]
        },
        "agent_interactions": [
            create_interaction(
                state, 
                agent="summarizer", 
                answer=final_content, 
                next_agent="end"
            )
        ]
    }
