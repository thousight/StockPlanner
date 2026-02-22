from pydantic import BaseModel, Field
from typing import List

class HighLevelPlan(BaseModel):
    steps: List[str] = Field(description="The sequence of high-level steps to be taken by which worker")
    next_worker: str = Field(description="The next specialized worker to call")