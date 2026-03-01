from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_db
from src.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Check the health of the application and database connectivity.
    """
    try:
        # Perform a simple query to verify database connectivity
        await db.execute(text("SELECT 1"))
        return HealthResponse(status="ok", database="connected")
    except Exception as e:
        # If the database is not connected, return an error
        raise HTTPException(
            status_code=503,
            detail=f"Database connectivity failed: {str(e)}"
        )
