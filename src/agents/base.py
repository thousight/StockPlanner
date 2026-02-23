from pydantic import BaseModel, Field

class BaseAgentResponse(BaseModel):
    """Base class for all structured agent responses."""
    next_agent: str = Field(description="The next specialized agent to call")
    next_question: str = Field(description="The specific instruction or question for the next agent")
    step_id: int = Field(description="The ID of the high-level plan step being fulfilled or initiated")
