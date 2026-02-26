from pydantic import Field
from src.agents.base import BaseAgentResponse

class OffTopicAnswer(BaseAgentResponse):
    answer: str = Field(description="Your answer to the user's question.")