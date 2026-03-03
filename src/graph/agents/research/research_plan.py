from pydantic import BaseModel, Field
from typing import List
from src.graph.utils.tool_call import ToolCall

class ResearchPlan(BaseModel):
    next_agent: str = Field(description="The next specialized agent to call")
    steps: List[ToolCall] = Field(description="Tool calls to fetch data points")