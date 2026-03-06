from pydantic import BaseModel, Field
from typing import List

class SupervisorResponse(BaseModel):
    """The response from the supervisor agent, determining the next steps."""
    next_agents: List[str] = Field(description="The list of next specialized agents to call in parallel")
