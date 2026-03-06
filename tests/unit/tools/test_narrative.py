import pytest
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timezone, timedelta
from src.graph.tools.narrative import (
    get_indices_performance, 
    get_historical_narrative, 
    synthesize_growth_narrative,
    NarrativeShift
)

@pytest.mark.asyncio
async def test_get_indices_performance():
    mock_hist = pd.DataFrame({'Close': [100.0, 105.0]}, index=[datetime.now(), datetime.now()])
    with patch("src.graph.tools.narrative.get_historical_prices_async", new_callable=AsyncMock) as mock_prices:
        mock_prices.return_value = mock_hist
        result = await get_indices_performance()
        assert "Major Indices Pulse" in result
        assert "SPY" in result
        assert mock_prices.call_count == 4

@pytest.mark.asyncio
async def test_get_historical_narrative_miss():
    with patch("src.graph.tools.narrative.AsyncSessionLocal") as mock_db:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        mock_db.return_value.__aenter__.return_value = mock_session
        
        result = await get_historical_narrative(subject="Gold")
        assert "DATA MISSING" in result
        assert "Gold" in result

@pytest.mark.asyncio
async def test_synthesize_growth_narrative():
    mock_shift = NarrativeShift(
        current_narrative="Bullish on Gold.",
        top_3_drivers=["Inflation", "War", "Central Banks"],
        sentiment_shift="Baseline shift.",
        confidence=0.9
    )
    with patch("langchain_openai.ChatOpenAI.with_structured_output") as mock_struct, \
         patch("src.graph.tools.narrative.AsyncSessionLocal") as mock_db:
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_shift
        mock_struct.return_value = mock_chain
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_db.return_value.__aenter__.return_value = mock_session
        
        result = await synthesize_growth_narrative(
            research_context="Some news about Gold. ### Previous Narrative\nPrevious Bullish stuff",
            subject="Gold"
        )
        
        assert "## Growth Narrative: Gold" in result
        assert "Bullish on Gold" in result
        assert "Inflation" in result
        mock_session.commit.assert_called_once()
