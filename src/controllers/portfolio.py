from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.schemas.portfolio import PortfolioSummary
from src.services.portfolio import get_portfolio_summary
from src.services.benchmarking import get_spy_performance

router = APIRouter(prefix="/investment", tags=["portfolio"])

@router.get("", response_model=PortfolioSummary)
async def get_portfolio_endpoint(
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """
    Get the overall portfolio summary, including performance metrics and sector allocation.
    """
    try:
        summary = await get_portfolio_summary(db, x_user_id)
        
        # Add benchmark comparison
        try:
            benchmark = await get_spy_performance(db, summary.total_gain_loss_pct)
            summary.benchmark = benchmark
        except Exception as e:
            print(f"Error fetching benchmark data: {e}")
            
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
