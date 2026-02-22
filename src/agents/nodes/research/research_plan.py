from pydantic import BaseModel, Field
from typing import List
from agents.utils.tool_call import ToolCall

class ResearchPlan(BaseModel):
    steps: List[ToolCall] = Field(description="Tool calls to fetch data points")