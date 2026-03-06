import pytest
from src.graph.graph import MeshRouter
from langgraph.types import Send

def test_mesh_router_single():
    router = MeshRouter(allowed_destinations=["analyst", "summarizer"])
    state = {
        "agent_interactions": [{"next_agent": "analyst"}]
    }
    result = router(state)
    assert result == "analyst"

def test_mesh_router_parallel():
    router = MeshRouter(allowed_destinations=["fundamental_researcher", "sentiment_researcher"])
    state = {
        "agent_interactions": [{"next_agent": "fundamental_researcher, sentiment_researcher"}]
    }
    result = router(state)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(r, Send) for r in result)
    assert result[0].node == "fundamental_researcher"
    assert result[1].node == "sentiment_researcher"

def test_mesh_router_invalid_fallback():
    router = MeshRouter(allowed_destinations=["summarizer"])
    state = {
        "agent_interactions": [{"next_agent": "invalid_agent"}]
    }
    result = router(state)
    assert result == "summarizer"
