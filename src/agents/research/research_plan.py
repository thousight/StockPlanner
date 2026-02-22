from pydantic import BaseModel, Field
from typing import List
from src.utils.tool_call import ToolCall

class ResearchPlan(BaseModel):
    steps: List[ToolCall] = Field(description="Tool calls to fetch data points")
    next_agent: str = Field(description="The next specialized agent to call or 'supervisor'")