from typing import List, Dict, Any, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    portfolio: List[Dict[str, Any]]
    research_data: Annotated[Dict[str, Any], operator.ior]
    user_question: str
    analysis_report: str
    next_node: str
    high_level_plan: List[str]
    debate_output: Dict[str, Any]
    analysis_cache_key: str
    revision_count: Annotated[int, operator.add]
