from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.state import AgentState
from src.agents.summarizer.prompts import SUMMARIZER_SYSTEM_PROMPT
from src.agents.utils import get_next_interaction_id, with_logging
from src.utils.prompt import convert_state_to_prompt

@with_logging
def summarizer_agent(state: AgentState):
    """
    Summarizer Agent: Reviews all agent interactions and synthesizes a final answer.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
    system_msg = SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state)
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
