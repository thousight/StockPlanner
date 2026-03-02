import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.graph.state import AgentState
from src.graph.agents.summarizer.prompts import SUMMARIZER_SYSTEM_PROMPT
from src.graph.utils.agents import get_next_interaction_id, with_logging
from src.graph.utils.prompt import convert_state_to_prompt

@with_logging
async def summarizer_agent(state: AgentState):
    """
    Summarizer Agent: Reviews all agent interactions and synthesizes a final answer.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
    system_msg = SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state)
    ))
        
    response = await llm.ainvoke([system_msg])
    final_content = response.content
    
    # Try to extract the symbol from user_input (basic regex for UPPERCASE 1-5 letters)
    user_input = state.get("user_input", "")
    symbol_match = re.search(r'\b[A-Z]{1,5}\b', user_input)
    symbol = symbol_match.group(0) if symbol_match else None
        
    return {
        "output": final_content,
        "pending_report": {
            "content": final_content,
            "symbol": symbol
        },
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "summarizer",
            "answer": final_content,
            "next_agent": "end"
        }]
    }
