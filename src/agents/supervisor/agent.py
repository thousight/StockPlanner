from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.agents.supervisor.prompts import SUPERVISOR_PROMPT, SUPERVISOR_PLAN_PROMPT
from src.agents.supervisor.response import SupervisorResponse
from src.utils.prompt import convert_state_to_prompt
from src.agents.supervisor.next_agents import get_supervisor_next_agents_prompt
from src.agents.utils import get_next_interaction_id, with_logging

@with_logging
def supervisor_agent(state: AgentState):
    """
    Strategic Investment Planner: Decides the initial step and routes to the appropriate agent.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(SupervisorResponse, method="function_calling")
    
    # Use utility functions for prompt context
    system_msg = SystemMessage(content=SUPERVISOR_PROMPT.format(
        current_context=convert_state_to_prompt(state),
        available_agents=get_supervisor_next_agents_prompt()
    ))
    human_msg = HumanMessage(content=SUPERVISOR_PLAN_PROMPT.format(dummy=""))
    
    # Construct message list: system prompt -> history -> current plan prompt
    messages = [system_msg, human_msg]
    
    # Loop Detection
    revision_count = state.get("revision_count", 0)
    if revision_count > 5:
        print("--- SUPERVISOR: Loop limit reached! Forcing an end... ---")
        return {
            "revision_count": 1,
            "agent_interactions": [{
                "id": get_next_interaction_id(state),
                "agent": "supervisor",
                "answer": "Loop limit reached",
                "next_agent": "summarizer"
            }]
        }
    
    plan_output = structured_llm.invoke(messages)
    
    return {
        "revision_count": 1,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "supervisor",
            "answer": f"Routed to {plan_output.next_agent}",
            "next_agent": plan_output.next_agent
        }]
    }
