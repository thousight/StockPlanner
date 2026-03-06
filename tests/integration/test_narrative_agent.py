import pytest
from datetime import datetime, timezone, timedelta
from src.graph.graph import create_graph
from src.database.session import AsyncSessionLocal
from src.database.models import ResearchCache, ResearchSourceType
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from src.config import settings

@pytest.mark.asyncio(loop_scope="function")
async def test_narrative_researcher_full_flow():
    """
    Integration test for NarrativeResearcher using atomic tools.
    """
    # 1. Setup - Clear Cache in a strictly managed fresh session with an isolated engine
    isolated_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    async with AsyncSession(isolated_engine) as db:
        await db.execute(delete(ResearchCache).where(ResearchCache.source_type == ResearchSourceType.NARRATIVE))
        await db.commit()
    await isolated_engine.dispose()

    graph = create_graph()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    initial_state = {
        "user_input": "What is the broad market growth narrative today?",
        "session_context": {
            "current_datetime": now.isoformat(),
            "user_agent": "Pytest-Integration-Tester",
            "messages": [],
            "revision_count": 0
        },
        "user_context": {
            "user_id": 1,
            "first_name": "Test",
            "risk_tolerance": "moderate",
            "base_currency": "USD",
            "portfolio": []
        },
        "agent_interactions": []
    }
    
    final_state = await graph.ainvoke(initial_state)
    interactions = final_state.get("agent_interactions", [])
    
    # Check if narrative researcher was called and has some output (could be intermediate search results or final synthesis)
    narrative_interaction = next((i for i in interactions if i["agent"] == "narrative_researcher"), None)
    assert narrative_interaction is not None
    # The researcher should have gathered data or synthesized it
    assert any(marker in narrative_interaction["answer"] for marker in ["Market Narrative", "Web Search", "Major Indices"])
