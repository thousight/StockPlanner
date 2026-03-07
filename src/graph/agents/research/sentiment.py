from typing import Optional
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from src.graph.state import AgentState
from src.graph.utils.prompt import convert_state_to_prompt, convert_tools_to_prompt
from src.graph.tools.news import get_stock_news, web_search
from src.graph.tools.sentiment import get_market_sentiment
from src.graph.agents.research.prompts import SENTIMENT_RESEARCHER_PROMPT, RESEARCH_PLANNER_PLAN_PROMPT
from src.graph.agents.research.research_plan import ResearchPlan
from src.graph.utils.agents import get_next_interaction_id, with_logging
from src.graph.agents.research.utils import execute_tool

TOOLS_LIST = [
    get_stock_news,
    get_market_sentiment,
    web_search
]

AVAILABLE_TOOLS_PROMPT = convert_tools_to_prompt(TOOLS_LIST)

@with_logging
async def sentiment_researcher(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Sentiment Research Specialist: Analyzes market mood from news and social media.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(ResearchPlan, method="function_calling")
    
    messages = [
        SystemMessage(content=SENTIMENT_RESEARCHER_PROMPT.format(
            current_context=convert_state_to_prompt(state),
            available_tools=AVAILABLE_TOOLS_PROMPT
        )),
        HumanMessage(content=RESEARCH_PLANNER_PLAN_PROMPT.format(dummy=""))
    ]
    
    local_plan = await structured_llm.ainvoke(messages)
    research_data = ""
    client_ua = state.get("session_context", {}).get("user_agent", "")

    # Execute tool calls
    tasks = [execute_tool(step, TOOLS_LIST, client_ua, local_plan.subject) for step in local_plan.steps]
    results = await asyncio.gather(*tasks)
    
    for result_str in results:
        if result_str:
            research_data += result_str + "\n"

    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "sentiment_researcher",
            "answer": research_data,
            "next_agent": "analyst"
        }]
    }
