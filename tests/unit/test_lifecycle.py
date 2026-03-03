import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from main import lifespan
from src.lifecycle.tasks import cleanup_checkpoints, cleanup_news_cache
import time_machine
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_lifespan_startup_shutdown():
    mock_app = MagicMock()
    mock_checkpointer = AsyncMock()
    
    # Patch dependencies inside lifespan
    with patch("main.get_checkpointer") as mock_get_cp:
        mock_get_cp.return_value.__aenter__.return_value = mock_checkpointer
        
        with patch("main.AsyncIOScheduler") as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            # Patch the engine object itself, as .dispose is read-only
            with patch("main.engine") as mock_engine:
                mock_engine.dispose = AsyncMock()
                
                # Use the context manager
                async with lifespan(mock_app):
                    # Verify startup
                    mock_get_cp.assert_called_once()
                    mock_checkpointer.setup.assert_called_once()
                    mock_scheduler.start.assert_called_once()
                    
                # Verify shutdown
                mock_scheduler.shutdown.assert_called_once()
                mock_engine.dispose.assert_called_once()

@pytest.mark.asyncio
async def test_cleanup_checkpoints_sql():
    mock_conn = MagicMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()
    
    mock_cur = MagicMock()
    mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
    mock_cur.__aexit__ = AsyncMock()
    mock_cur.execute = AsyncMock()
    
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit = AsyncMock()
    
    # This matches: async with await psycopg.AsyncConnection.connect(...)
    async def mock_connect(*args, **kwargs):
        return mock_conn
    
    with patch("psycopg.AsyncConnection.connect", side_effect=mock_connect):
        with patch("src.lifecycle.tasks.get_checkpointer_conn_string", return_value="dsn"):
            await cleanup_checkpoints()
            
            # Verify SQL calls
            calls = mock_cur.execute.call_args_list
            assert any("DELETE FROM checkpoints" in str(c) for c in calls)
            assert any("DELETE FROM checkpoint_writes" in str(c) for c in calls)
            assert mock_conn.commit.called

@pytest.mark.asyncio
async def test_cleanup_news_cache_time():
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
            with patch("src.lifecycle.tasks.get_checkpointer_conn_string", return_value="dsn"):
                await cleanup_news_cache()
                
                # Verify it called execute with the fixed time (ignoring microseconds if any)
                mock_cur.execute.assert_called_once()
                args, kwargs = mock_cur.execute.call_args
                assert "DELETE FROM news_cache" in args[0]
                assert args[1][0].replace(microsecond=0) == fixed_now
