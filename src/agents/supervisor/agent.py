from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.agents.supervisor.prompts import SUPERVISOR_PROMPT, SUPERVISOR_PLAN_PROMPT
from src.agents.supervisor.high_level_plan import HighLevelPlan
from src.utils.prompt import convert_state_to_prompt
from src.agents.supervisor.next_agents import get_supervisor_next_agents_prompt
from src.agents.utils import get_next_interaction_id, get_current_question

def supervisor_agent(state: AgentState):
    """
    Strategic Investment Planner: Decomposes user request and orchestrates agents.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(HighLevelPlan, method="function_calling")
    
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
                "step_id": 0, # Loop limit is global
                "agent": "supervisor",
                "question": get_current_question(state, "Loop check"),
                "answer": "Loop limit reached",
                "next_agent": "summarizer",
                "next_question": "Summarize the current state and explain the loop limit was reached."
            }]
        }
    
    plan_output = structured_llm.invoke(messages)
    
    print(f"--- SUPERVISOR PLAN: {plan_output.steps} ---")
    print(f"--- NEXT AGENT: {plan_output.next_agent} ---")
    
    # Store steps as list of dicts for state compatibility
    structured_steps = [s.model_dump() for s in plan_output.steps]

    return {
        "high_level_plan": structured_steps,
        "revision_count": 1,
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "step_id": plan_output.step_id, # The step we are initiating
            "agent": "supervisor",
            "question": get_current_question(state, "Decompose request"),
            "answer": str(plan_output.steps),
            "next_agent": plan_output.next_agent,
            "next_question": plan_output.next_question
        }]
    }
