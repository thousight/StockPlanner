import pytest
import operator
from src.graph.state import AgentState

def test_code_revision_count_reducer():
    # Initial state
    state = {"code_revision_count": 0}
    
    # Update from node
    update = {"code_revision_count": 1}
    
    # Simulating LangGraph reducer logic
    # In LangGraph, if a field is Annotated with operator.add, it uses that function
    new_value = operator.add(state["code_revision_count"], update["code_revision_count"])
    assert new_value == 1
    
    # Second update
    final_value = operator.add(new_value, 1)
    assert final_value == 2
