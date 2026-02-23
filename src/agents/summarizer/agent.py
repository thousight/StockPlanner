from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.state import AgentState
from src.agents.summarizer.prompts import SUMMARIZER_SYSTEM_PROMPT
from src.agents.utils import format_interactions_as_text, get_next_interaction_id, get_current_question

def summarizer_agent(state: AgentState):
    """
    Summarizer Agent: Reviews all agent interactions and synthesizes a final answer.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_msg = SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT.format(
        user_input=state.get("user_input", ""),
        agent_interactions=format_interactions_as_text(state)
    ))
    
    response = llm.invoke([system_msg])
    
    # Infer step_id from the supervisor's instruction if possible
    interactions = state.get("agent_interactions", [])
    step_id = interactions[-1].get("step_id", 0) if interactions else 0

    return {
        "output": response.content,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "step_id": step_id,
            "agent": "summarizer",
            "question": get_current_question(state, "Summarize the findings"),
            "answer": response.content,
            "next_agent": "end",
            "next_question": "Final response delivered to user."
        }]
    }
