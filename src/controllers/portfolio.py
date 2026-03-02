from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.schemas.portfolio import PortfolioSummary
from src.services.portfolio import get_portfolio_summary
from src.services.benchmarking import get_spy_performance

router = APIRouter(prefix="/investment", tags=["portfolio"])

@router.get("", response_model=PortfolioSummary)
def get_portfolio_endpoint(db: Session = Depends(get_db)):
    """
    Get the overall portfolio summary, including performance metrics and sector allocation.
    """
    user_id = "default_user"
    try:
        summary = get_portfolio_summary(db, user_id)
        
        # Add benchmark comparison
        try:
            benchmark = get_spy_performance(db, summary.total_gain_loss_pct)
            summary.benchmark = benchmark
        except Exception as e:
            print(f"Error fetching benchmark data: {e}")
            
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
