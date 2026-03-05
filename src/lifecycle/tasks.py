import psycopg
import logging
from datetime import datetime, timezone
from src.config import settings

logger = logging.getLogger(__name__)

async def cleanup_research_cache():
    """
    Deletes expired entries from the research_cache table in PostgreSQL.
    """
    # psycopg3 expects standard postgresql:// schema
    conn_string = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    try:
        async with await psycopg.AsyncConnection.connect(conn_string) as conn:
            async with conn.cursor() as cur:
                logger.info("Starting cleanup of expired research cache entries...")
                
                # Delete rows where expire_at is in the past
                await cur.execute(
                    "DELETE FROM research_cache WHERE expire_at < %s", 
                    (datetime.now(timezone.utc).replace(tzinfo=None),)
                )
                deleted_count = cur.rowcount
                
                await conn.commit()
                logger.info(f"Research cache cleanup completed: {deleted_count} entries removed.")
    except Exception as e:
        logger.error(f"Error during research cache cleanup: {e}")
