from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState
from src.agents.utils.news import get_stock_news, get_macro_economic_news, web_search
from src.agents.utils.prompt_utils import convert_state_to_prompt, convert_tools_to_prompt
from .utils import get_stock_financials
from .prompts import RESEARCH_PLANNER_SYSTEM_PROMPT, RESEARCH_PLANNER_PLAN_PROMPT
from .research_plan import ResearchPlan

AVAILABLE_TOOLS = [
    get_stock_financials,
    get_stock_news,
    get_macro_economic_news,
    web_search
]

def research_node(state: AgentState):
    """
    Research agent: Performs local planning and executes research tools.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(ResearchPlan)
    
    # Use utility functions for prompt context
    current_context = convert_state_to_prompt(state)
    available_tools = convert_tools_to_prompt(AVAILABLE_TOOLS)
    
    messages = [
        SystemMessage(content=RESEARCH_PLANNER_SYSTEM_PROMPT.format(
            current_context=current_context,
            available_tools=available_tools
        )),
        HumanMessage(content=RESEARCH_PLANNER_PLAN_PROMPT)
    ]
    
    local_plan = structured_llm.invoke(messages)
    print(f"--- RESEARCH LOCAL PLAN: {local_plan.steps} ---")
    
    research_data = {}

    for step in local_plan.steps:
        tool = AVAILABLE_TOOLS[step.tool_name]
        research_data[step.tool_name] = tool.invoke(step.tool_params)

    return {
        "research_data": research_data,
        "next_node": "supervisor"
    }
