from pydantic import BaseModel, Field

class BaseAgentResponse(BaseModel):
    """Base class for all structured agent responses."""
    next_agent: str = Field(description="The next specialized agent to call")
