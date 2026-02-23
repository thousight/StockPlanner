from pydantic import Field
from src.agents.base import BaseAgentResponse

class OffTopicAnswer(BaseAgentResponse):
    reasoning: str = Field(description="Your internal reasoning for how to handle the user's input, or a message to the next agent.")