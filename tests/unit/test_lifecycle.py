import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from main import lifespan
from src.lifecycle.tasks import cleanup_research_cache
import time_machine
from datetime import datetime

@pytest.mark.asyncio
async def test_lifespan_startup_shutdown():
    mock_app = MagicMock()
    
    # Patch dependencies inside lifespan
    with patch("main.get_checkpointer") as mock_get_cp:
        # get_checkpointer returns an AsyncRedisSaver (async context manager)
        mock_checkpointer = AsyncMock()
        mock_checkpointer.__aenter__.return_value = mock_checkpointer
        mock_get_cp.return_value = mock_checkpointer
        
        with patch("main.AsyncIOScheduler") as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            # Patch the engine object itself, as .dispose is read-only
            with patch("main.engine") as mock_engine:
                mock_engine.dispose = AsyncMock()
                
                # Patch redis health check
                with patch("main.redis_cb.call_async", new_callable=AsyncMock) as mock_cb_call:
                    # Use the context manager
                    async with lifespan(mock_app):
                        # Verify startup
                        mock_get_cp.assert_called_once()
                        mock_checkpointer.setup.assert_called_once()
                        mock_scheduler.start.assert_called_once()
                        mock_cb_call.assert_called_once()
                        
                    # Verify shutdown
                    mock_scheduler.shutdown.assert_called_once()
                    mock_engine.dispose.assert_called_once()

@pytest.mark.asyncio
async def test_cleanup_research_cache_time():
    mock_conn = MagicMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()
    
    mock_cur = MagicMock()
    mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
    mock_cur.__aexit__ = AsyncMock()
    mock_cur.execute = AsyncMock()
    
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit = AsyncMock()
    
    async def mock_connect(*args, **kwargs):
        return mock_conn

    # Set fixed time
    fixed_now = datetime(2023, 1, 1, 12, 0, 0)
    
    with time_machine.travel(fixed_now):
        with patch("psycopg.AsyncConnection.connect", side_effect=mock_connect):
            await cleanup_research_cache()
            
            # Verify it called execute with the fixed time (ignoring microseconds if any)
            mock_cur.execute.assert_called_once()
            args, kwargs = mock_cur.execute.call_args
            assert "DELETE FROM research_cache" in args[0]
            assert args[1][0].replace(microsecond=0) == fixed_now
