from pydantic import BaseModel, Field
from typing import List
from src.agents.base import BaseAgentResponse

class PlanStep(BaseModel):
    id: int = Field(description="Unique ID for the plan step")
    description: str = Field(description="Description of what should be done in this step")

class HighLevelPlan(BaseAgentResponse):
    steps: List[PlanStep] = Field(description="The sequence of high-level steps to be taken")