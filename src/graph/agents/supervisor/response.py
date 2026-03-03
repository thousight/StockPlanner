from pydantic import BaseModel, Field

class SupervisorResponse(BaseModel):
    """The response from the supervisor agent, determining the next step."""
    next_agent: str = Field(description="The next specialized agent to call")