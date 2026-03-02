import psycopg
import logging
from datetime import datetime, timezone
from src.graph.persistence import get_checkpointer_conn_string

logger = logging.getLogger(__name__)

async def cleanup_checkpoints():
    """
    Deletes checkpoints older than 30 days and cleans up orphaned blobs/writes.
    """
    conn_string = get_checkpointer_conn_string()
    try:
        async with await psycopg.AsyncConnection.connect(conn_string) as conn:
            async with conn.cursor() as cur:
                logger.info("Starting cleanup of old LangGraph checkpoints (30-day TTL)...")
                
                # Delete checkpoints older than 30 days
                # LangGraph 0.2+ AsyncPostgresSaver uses 'ts' for timestamp
                await cur.execute(
                    "DELETE FROM checkpoints WHERE ts < (NOW() - INTERVAL '30 days')"
                )
                deleted_checkpoints = cur.rowcount
                
                # Cleanup orphaned writes and blobs to prevent storage leaks
                await cur.execute("""
                    DELETE FROM checkpoint_writes 
                    WHERE thread_id NOT IN (SELECT thread_id FROM checkpoints);
                """)
                deleted_writes = cur.rowcount
                
                await cur.execute("""
                    DELETE FROM checkpoint_blobs 
                    WHERE thread_id NOT IN (SELECT thread_id FROM checkpoints);
                """)
                deleted_blobs = cur.rowcount
                
                await conn.commit()
                logger.info(
                    f"Checkpoint cleanup completed: {deleted_checkpoints} checkpoints, "
                    f"{deleted_writes} writes, {deleted_blobs} blobs removed."
                )
    except Exception as e:
        logger.error(f"Error during checkpoint cleanup: {e}")

async def cleanup_news_cache():
    """
    Deletes expired entries from the news_cache table.
    """
    conn_string = get_checkpointer_conn_string()
    try:
        async with await psycopg.AsyncConnection.connect(conn_string) as conn:
            async with conn.cursor() as cur:
                logger.info("Starting cleanup of expired news cache entries...")
                
                # Delete rows where expire_at is in the past
                await cur.execute(
                    "DELETE FROM news_cache WHERE expire_at < %s", 
                    (datetime.now(timezone.utc).replace(tzinfo=None),)
                )
                deleted_count = cur.rowcount
                
                await conn.commit()
                logger.info(f"News cache cleanup completed: {deleted_count} entries removed.")
    except Exception as e:
        logger.error(f"Error during news cache cleanup: {e}")
