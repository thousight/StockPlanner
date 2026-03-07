import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.graph.state import AgentState
from src.graph.agents.supervisor.prompts import SUPERVISOR_PROMPT, SUPERVISOR_PLAN_PROMPT
from src.graph.agents.supervisor.response import SupervisorResponse
from src.graph.utils.prompt import convert_state_to_prompt
from src.graph.agents.supervisor.next_agents import get_supervisor_next_agents_prompt
from src.graph.utils.agents import create_interaction, get_llm, get_session_info, with_logging

logger = logging.getLogger(__name__)

@with_logging
async def supervisor_agent(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Strategic Investment Planner: Decides the initial step and routes to the appropriate agents.
    """
    llm = get_llm(temperature=0)
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
    revision_count = state.get("session_context", {}).get("revision_count", 0)
    if revision_count > 5:
        logger.warning("SUPERVISOR: Loop limit reached! Forcing an end...")
        return {
            "session_context": {"revision_count": 1},
            "agent_interactions": [
                create_interaction(
                    state, 
                    agent="supervisor", 
                    answer="Loop limit reached", 
                    next_agent="summarizer"
                )
            ]
        }
    
    plan_output = await structured_llm.ainvoke(messages)
    
    # next_agent is kept for legacy compatibility with routers that expect a single string
    # We join them with a comma for parallel nodes
    next_agent_str = ",".join(plan_output.next_agents) if plan_output.next_agents else "summarizer"
    
    return {
        "session_context": {"revision_count": 1},
        "agent_interactions": [
            create_interaction(
                state, 
                agent="supervisor", 
                answer=f"Routed to {next_agent_str}", 
                next_agent=next_agent_str
            )
        ]
    }
