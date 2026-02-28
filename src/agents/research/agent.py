import inspect
import concurrent.futures
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.utils.prompt import convert_state_to_prompt, convert_tools_to_prompt
from src.tools.news import get_stock_news, get_macro_economic_news, web_search
from src.tools.research import get_stock_financials
from src.agents.research.prompts import RESEARCH_PLANNER_SYSTEM_PROMPT, RESEARCH_PLANNER_PLAN_PROMPT
from src.agents.research.research_plan import ResearchPlan
from src.agents.research.next_agents import get_research_next_agents_prompt
from src.agents.utils import get_next_interaction_id, with_logging

TOOLS_LIST = [
    get_stock_financials,
    get_stock_news,
    get_macro_economic_news,
    web_search
]

AVAILABLE_TOOLS_PROMPT = convert_tools_to_prompt(TOOLS_LIST)

@with_logging
def research_agent(state: AgentState):
    """
    Research agent: Plan a research based on the research question, and execute the research tools.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(ResearchPlan, method="function_calling")
    
    messages = [
        SystemMessage(content=RESEARCH_PLANNER_SYSTEM_PROMPT.format(
            current_context=convert_state_to_prompt(state),
            available_tools=AVAILABLE_TOOLS_PROMPT,
            available_next_agents=get_research_next_agents_prompt()
        )),
        HumanMessage(content=RESEARCH_PLANNER_PLAN_PROMPT.format(dummy=""))
    ]
    
    local_plan = structured_llm.invoke(messages)
    research_data = ""

    # Extract user_agent for downstream tool propagation
    client_ua = state.get("session_context", {}).get("user_agent", "")

    # Run tool calls in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_tool, step, client_ua) for step in local_plan.steps]
        for future in concurrent.futures.as_completed(futures):
            result_str = future.result()
            if result_str:
                research_data += result_str + "\n"

    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "research",
            "answer": research_data,
            "next_agent": local_plan.next_agent
        }]
    }
    
def execute_tool(step, user_agent=""):
    # Build a lookup mapping for tool names from the actual function list
    tool_map = {tool.__name__: tool for tool in TOOLS_LIST}
    tool = tool_map.get(step.tool_name)
    if tool:
        try:
            # Check if the tool accepts a user_agent parameter or **kwargs
            sig = inspect.signature(tool)
            accepts_kwargs = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            
            if "user_agent" in sig.parameters or accepts_kwargs:
                step.tool_params["user_agent"] = user_agent
                
            # Quick fix for web_search arguments
            if step.tool_name == "web_search":
                if "query" in step.tool_params and "queries" not in step.tool_params:
                    step.tool_params["queries"] = [step.tool_params.pop("query")]
                elif "q" in step.tool_params and "queries" not in step.tool_params:
                    step.tool_params["queries"] = [step.tool_params.pop("q")]
                elif "queries" in step.tool_params and isinstance(step.tool_params["queries"], str):
                    step.tool_params["queries"] = [step.tool_params["queries"]]
                elif "queries" not in step.tool_params:
                    # Fallback if somehow it's empty but called
                    step.tool_params["queries"] = ["latest market news"]
                
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