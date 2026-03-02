from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from src.config import settings
from src.middleware import ExcludeNoneRoute
from src.database.session import engine
from src.controllers.health import router as health_router
from src.controllers.transactions import router as transactions_router
from src.controllers.portfolio import router as portfolio_router
from src.controllers.chat import router as chat_router
from src.controllers.reports import router as reports_router
from src.lifecycle.tasks import cleanup_checkpoints, cleanup_news_cache
from src.graph.persistence import get_checkpointer

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Global set for thread concurrency protection
active_threads = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    
    # Initialize LangGraph checkpointer tables
    try:
        async with get_checkpointer() as checkpointer:
            # setup() creates the tables if they don't exist
            await checkpointer.setup()
        logger.info("LangGraph persistence tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LangGraph persistence: {e}")

    # Setup Scheduler
    scheduler = AsyncIOScheduler()
    
    # Schedule checkpoint cleanup: Daily at 02:00 AM
    scheduler.add_job(
        cleanup_checkpoints,
        CronTrigger(hour=2, minute=0),
        id="cleanup_checkpoints",
        name="Daily LangGraph checkpoint cleanup (30-day TTL)",
        replace_existing=True
    )
    
    # Schedule news cache cleanup: Hourly
    scheduler.add_job(
        cleanup_news_cache,
        "interval",
        hours=1,
        id="cleanup_news_cache",
        name="Hourly news cache cleanup",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background task scheduler started")
    
    yield
    # Shutdown logic
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    
    scheduler.shutdown()
    logger.info("Background task scheduler shut down")
    
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Apply global route class for excluding None/null fields
app.router.route_class = ExcludeNoneRoute

@app.middleware("http")
async def thread_concurrency_protection(request: Request, call_next):
    """
    Protects against concurrent runs for the same thread_id.
    Looks for 'X-Thread-ID' in request headers.
    """
    thread_id = request.headers.get("X-Thread-ID")
    
    # We only apply this to potential chat/graph endpoints
    if thread_id and ("/chat" in request.url.path or "/graph" in request.url.path):
        if thread_id in active_threads:
            logger.warning(f"Rejecting concurrent request for thread_id: {thread_id}")
            return JSONResponse(
                status_code=409,
                content={"detail": f"Conflict: Thread {thread_id} is already being processed."}
            )
        
        active_threads.add(thread_id)
        try:
            response = await call_next(request)
            return response
        finally:
            active_threads.discard(thread_id)
    
    return await call_next(request)

# Add correlation ID middleware for request tracking
app.add_middleware(CorrelationIdMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(transactions_router)
app.include_router(portfolio_router)
app.include_router(chat_router)
app.include_router(reports_router)

@app.get("/")
async def root():
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
