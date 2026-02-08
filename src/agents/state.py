from typing import List, Dict, Any, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    portfolio: List[Dict[str, Any]]
    research_data: Dict[str, Any]
    analysis_report: str
