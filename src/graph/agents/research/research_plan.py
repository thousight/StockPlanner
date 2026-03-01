from pydantic import Field
from typing import List
from src.graph.agents.base import BaseAgentResponse
from src.graph.utils.tool_call import ToolCall

class ResearchPlan(BaseAgentResponse):
    steps: List[ToolCall] = Field(description="Tool calls to fetch data points")