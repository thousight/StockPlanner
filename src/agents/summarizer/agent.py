from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.state import AgentState
from src.agents.summarizer.prompts import SUMMARIZER_SYSTEM_PROMPT
from src.agents.utils import format_interactions_as_text, get_next_interaction_id, with_logging

@with_logging
def summarizer_agent(state: AgentState):
    """
    Summarizer Agent: Reviews all agent interactions and synthesizes a final answer.
    """
    interactions = state.get("agent_interactions", [])
    
    # If there is only one substantive interaction and it's already short enough, we can bypass
    last_answer = interactions[-1].get("answer", "") if interactions else ""
    if len(interactions) <= 2 and interactions and len(last_answer) < 800:
        final_content = last_answer
    else:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        system_msg = SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT.format(
            user_input=state.get("user_input", ""),
            agent_interactions=format_interactions_as_text(state)
        ))
        
        response = llm.invoke([system_msg])
        final_content = response.content
        
    return {
        "output": final_content,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "summarizer",
            "answer": final_content,
            "next_agent": "end"
        }]
    }
