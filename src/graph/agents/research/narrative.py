import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.graph.state import AgentState
from src.graph.utils.prompt import convert_state_to_prompt, convert_tools_to_prompt
from src.graph.tools.narrative import (
    get_indices_performance, 
    get_historical_narrative, 
    synthesize_growth_narrative
)
from src.graph.tools.news import get_stock_news, web_search
from src.graph.agents.research.prompts import NARRATIVE_RESEARCHER_PROMPT, RESEARCH_PLANNER_PLAN_PROMPT
from src.graph.agents.research.research_plan import ResearchPlan
from src.graph.utils.agents import get_next_interaction_id, with_logging
from src.graph.agents.research.utils import execute_tool

TOOLS_LIST = [
    get_indices_performance,
    get_historical_narrative,
    get_stock_news,
    web_search,
    synthesize_growth_narrative
]

AVAILABLE_TOOLS_PROMPT = convert_tools_to_prompt(TOOLS_LIST)

@with_logging
async def narrative_researcher(state: AgentState):
    """
    Narrative Research Specialist: Analyzes growth narratives and narrative shifts.
    Decides which data points to gather (indices, news, history) before synthesizing.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(ResearchPlan, method="function_calling")
    
    messages = [
        SystemMessage(content=NARRATIVE_RESEARCHER_PROMPT.format(
            current_context=convert_state_to_prompt(state),
            available_tools=AVAILABLE_TOOLS_PROMPT
        )),
        HumanMessage(content=RESEARCH_PLANNER_PLAN_PROMPT.format(dummy=""))
    ]
    
    local_plan = await structured_llm.ainvoke(messages)
    research_data = ""
    client_ua = state.get("session_context", {}).get("user_agent", "")

    # Execute tool calls
    # Improved execute_tool now handles the mapping internally if we pass the subject
    tasks = [execute_tool(step, TOOLS_LIST, client_ua, local_plan.subject) for step in local_plan.steps]
    results = await asyncio.gather(*tasks)
    
    for result_str in results:
        if result_str:
            research_data += result_str + "\n"

    # Store the final synthesized report or context
    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "narrative_researcher",
            "answer": research_data,
            "next_agent": "analyst"
        }],
        "market_context": research_data
    }
