from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from .prompts import SUPERVISOR_PROMPT, SUPERVISOR_PLAN_PROMPT
from .high_level_plan import HighLevelPlan
from src.utils.prompt import convert_state_to_prompt, convert_agents_to_prompt
from src.agents.research.agent import research_agent
from src.agents.analyst.agent import analyst_agent
from src.agents.cache_maintenance.agent import cache_maintenance_agent

# Define the available agents
AVAILABLE_AGENTS = {
    "research": research_agent,
    "analyst": analyst_agent,
    "cache_maintenance": cache_maintenance_agent
}

def supervisor_agent(state: AgentState):
    """
    Strategic Investment Planner: Decomposes user request and orchestrates agents.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(HighLevelPlan, method="function_calling")
    
    # Use utility functions for prompt context
    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT.format(
            current_context=convert_state_to_prompt(state),
            available_agents=convert_agents_to_prompt(AVAILABLE_AGENTS)
        )),
        HumanMessage(content=SUPERVISOR_PLAN_PROMPT)
    ]
    
    # Loop Detection
    revision_count = state.get("revision_count", 0)
    if revision_count > 5:
        print("--- SUPERVISOR: Loop limit reached! Forcing an end... ---")
        return {
            "next_agent": "cache_maintenance",
            "revision_count": 1 
        }
    
    plan_output = structured_llm.invoke(messages)
    
    print(f"--- SUPERVISOR PLAN: {plan_output.steps} ---")
    print(f"--- NEXT AGENT: {plan_output.next_agent} ---")
    
    return {
        "high_level_plan": plan_output.steps,
        "next_agent": plan_output.next_agent,
        "revision_count": 1
    }
