from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.schemas.portfolio import PortfolioSummary
from src.services.portfolio import get_portfolio_summary
from src.services.benchmarking import get_spy_performance
from src.services.auth import set_user_context
from src.database.models import User

router = APIRouter(prefix="/investment", tags=["portfolio"])

@router.get("", response_model=PortfolioSummary)
async def get_portfolio_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Get the overall portfolio summary, including performance metrics and sector allocation.
    """
    try:
        summary = await get_portfolio_summary(db, current_user.id)
        
        # Add benchmark comparison
        try:
            benchmark = await get_spy_performance(db, summary.total_gain_loss_pct)
            summary.benchmark = benchmark
        except Exception as e:
            print(f"Error fetching benchmark data: {e}")
            
        return summary
    except Exception as e:
        # Check if the service layer raised an exception that might indicate a missing user/data
        # Portfolio summary usually returns defaults if not found, 
        # but if we wanted stealth 404 for specific objects we'd do it here.
        # Since this is a root resource (portfolio summary for current user), 
        # we don't return 404 if the user exists but has no data, we return 0 values usually.
        raise HTTPException(status_code=500, detail=str(e))
