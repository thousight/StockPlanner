import asyncio
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.graph.state import AgentState
from src.graph.utils.prompt import convert_state_to_prompt, convert_tools_to_prompt
from src.graph.tools.sec import get_sec_filing_section, get_sec_filing_delta
from src.graph.tools.research import get_stock_financials
from src.graph.tools.news import web_search
from src.graph.agents.research.prompts import FUNDAMENTAL_RESEARCHER_PROMPT, RESEARCH_PLANNER_PLAN_PROMPT
from src.graph.agents.research.research_plan import ResearchPlan
from src.graph.utils.agents import get_llm, get_session_info, create_interaction, with_logging

TOOLS_LIST = [
    get_stock_financials,
    get_sec_filing_section,
    get_sec_filing_delta,
    web_search
]

AVAILABLE_TOOLS_PROMPT = convert_tools_to_prompt(TOOLS_LIST)

@with_logging
async def fundamental_researcher(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Fundamental Research Specialist: Analyzes financial statements and SEC filings.
    """
    llm = get_llm(temperature=0)
    info = get_session_info(state)
    structured_llm = llm.with_structured_output(ResearchPlan, method="function_calling")
    
    messages = [
        SystemMessage(content=FUNDAMENTAL_RESEARCHER_PROMPT.format(
            current_context=convert_state_to_prompt(state),
            available_tools=AVAILABLE_TOOLS_PROMPT
        )),
        HumanMessage(content=RESEARCH_PLANNER_PLAN_PROMPT.format(dummy=""))
    ]
    
    local_plan = await structured_llm.ainvoke(messages)
    research_data = ""

    # Execute tool calls
    from src.graph.agents.research.utils import execute_tool
    tasks = [execute_tool(step, TOOLS_LIST, info["user_agent"], local_plan.subject) for step in local_plan.steps]
    results = await asyncio.gather(*tasks)
    
    for result_str in results:
        if result_str:
            research_data += result_str + "\n"

    return {
        "agent_interactions": [
            create_interaction(
                state, 
                agent="fundamental_researcher", 
                answer=research_data, 
                next_agent="analyst"
            )
        ]
    }
