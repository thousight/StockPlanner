from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState
from .prompts import SUPERVISOR_PROMPT, SUPERVISOR_PLAN_PROMPT
from .high_level_plan import HighLevelPlan
from src.agents.utils.prompt_utils import convert_state_to_prompt, convert_agents_to_prompt
from src.agents.nodes.research.node import research_node
from src.agents.nodes.analyst.node import analyst_node
from src.agents.nodes.nodes import cache_maintenance_node

# Define the available nodes
AVAILABLE_NODES = {
    "research": research_node,
    "analyst": analyst_node,
    "cache_maintenance": cache_maintenance_node
}

def supervisor_node(state: AgentState):
    """
    Strategic Investment Planner: Decomposes user request and orchestrates workers.
    """
    llm = ChatOpenAI(model="gpt-5", temperature=0)
    structured_llm = llm.with_structured_output(HighLevelPlan)
    
    # Use utility functions for prompt context
    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT.format(
            current_context=convert_state_to_prompt(state),
            available_workers=convert_agents_to_prompt(AVAILABLE_NODES)
        )),
        HumanMessage(content=SUPERVISOR_PLAN_PROMPT)
    ]
    
    # Loop Detection
    revision_count = state.get("revision_count", 0)
    if revision_count > 5:
        print("--- SUPERVISOR: Loop limit reached! Forcing an end... ---")
        return {
            "next_node": "cache_maintenance",
            "revision_count": 1 
        }
    
    plan_output = structured_llm.invoke(messages)
    
    print(f"--- SUPERVISOR PLAN: {plan_output.steps} ---")
    print(f"--- NEXT WORKER: {plan_output.next_worker} ---")
    
    return {
        "high_level_plan": plan_output.steps,
        "next_node": plan_output.next_worker,
        "revision_count": 1
    }
