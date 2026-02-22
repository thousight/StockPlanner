from pydantic import BaseModel, Field
from typing import List

class HighLevelPlan(BaseModel):
    steps: List[str] = Field(description="The sequence of high-level steps to be taken by which agent")
    next_agent: str = Field(description="The next specialized agent to call")