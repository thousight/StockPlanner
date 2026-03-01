from pydantic import BaseModel, Field
from typing import Dict, Any

class ToolCall(BaseModel):
    tool_name: str = Field(description="Name of the tool to call")
    tool_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool as a dictionary of keyword arguments (e.g. {'symbol': 'AAPL'})")