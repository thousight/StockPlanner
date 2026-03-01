from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.middleware import ExcludeNoneRoute
from src.database.session import engine, Base
from src.database import models  # Ensure models are registered
from src.controllers.health import router as health_router

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    
    yield
    # Shutdown logic
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Apply global route class for excluding None/null fields
app.router.route_class = ExcludeNoneRoute

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

@app.get("/")
async def root():
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
