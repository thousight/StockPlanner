from pydantic import BaseModel, Field

class OffTopicAnswer(BaseModel):
    next_agent: str = Field(description="The next specialized agent to call")
    answer: str = Field(description="Your answer to the user's question.")