import concurrent.futures
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.utils.prompt import convert_state_to_prompt, convert_tools_to_prompt
from src.tools.news import get_stock_news, get_macro_economic_news, web_search
from src.tools.research import get_stock_financials
from .prompts import RESEARCH_PLANNER_SYSTEM_PROMPT, RESEARCH_PLANNER_PLAN_PROMPT
from .research_plan import ResearchPlan

AVAILABLE_TOOLS = [
    get_stock_financials,
    get_stock_news,
    get_macro_economic_news,
    web_search
]

def research_agent(state: AgentState):
    """
    Research agent: Performs local planning and executes research tools.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(ResearchPlan, method="function_calling")
    
    # Use utility functions for prompt context
    current_context = convert_state_to_prompt(state)
    available_tools = convert_tools_to_prompt(AVAILABLE_TOOLS)
    
    messages = [
        SystemMessage(content=RESEARCH_PLANNER_SYSTEM_PROMPT.format(
            current_context=current_context,
            available_tools=available_tools,
            available_next_agents="supervisor, analyst"
        )),
        HumanMessage(content=RESEARCH_PLANNER_PLAN_PROMPT)
    ]
    
    local_plan = structured_llm.invoke(messages)
    print(f"--- RESEARCH LOCAL PLAN: {local_plan.steps} ---")
    
    research_data = ""  

    # Run tool calls in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_tool, step) for step in local_plan.steps]
        for future in concurrent.futures.as_completed(futures):
            result_str = future.result()
            if result_str:
                research_data += result_str + "\n"

    return {
        "research_data": research_data,
        "next_agent": local_plan.next_agent
    }
    
def execute_tool(step):
    # Build a lookup mapping for tool names
    tool_map = {tool.__name__: tool for tool in AVAILABLE_TOOLS}
    tool = tool_map.get(step.tool_name)
    if tool:
        try:
            # Execute standard function with unpacked dictionary parameters
            result = tool(**step.tool_params)
            if isinstance(result, str):
                return result
            return str(result) + "\n"
        except Exception as e:
            print(f"Error executing tool {step.tool_name}: {e}")
            return f"Error executing tool {step.tool_name}: {e}\n"
    else:
            print(f"Tool {step.tool_name} not found.")
            return f"Tool {step.tool_name} not found.\n"