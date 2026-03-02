import re
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.graph.state import AgentState
from src.graph.agents.summarizer.prompts import SUMMARIZER_SYSTEM_PROMPT
from src.graph.utils.agents import get_next_interaction_id, with_logging
from src.graph.utils.prompt import convert_state_to_prompt
from src.services.complexity import evaluate_complexity

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
async def summarizer_agent(state: AgentState):
    """
    Summarizer Agent: Reviews all agent interactions and synthesizes a final answer with metadata.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(SummarizerOutput)
        
    system_msg = SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state)
    ))
        
    response = await structured_llm.ainvoke([system_msg])
    final_content = response.final_answer
    
    # Calculate complexity score
    complexity_score = evaluate_complexity(final_content)
    
    # Try to extract the symbol from user_input (basic regex for UPPERCASE 1-5 letters)
    user_input = state.get("user_input", "")
    symbol_match = re.search(r'\b[A-Z]{1,5}\b', user_input)
    symbol = symbol_match.group(0) if symbol_match else None
        
    return {
        "output": final_content,
        "pending_report": {
            "title": response.title,
            "category": response.category,
            "topic": response.topic,
            "symbol": symbol,
            "tags": response.tags,
            "content": final_content,
            "complexity_score": complexity_score
        },
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "summarizer",
            "answer": final_content,
            "next_agent": "end"
        }]
    }
