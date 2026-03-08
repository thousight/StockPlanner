from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.database.models import Holding
from src.schemas.portfolio import PortfolioSummary
from src.services.portfolio import get_portfolio_summary, get_current_price

def format_portfolio_for_llm(summary: PortfolioSummary) -> str:
    """
    Formats a PortfolioSummary object into a concise text block for LLM consumption.
    Injected into AgentState.user_context['portfolio_summary'].
    """
    # Sort sectors by percentage descending and take top 3
    sorted_sectors = sorted(summary.sector_allocation, key=lambda s: s.percentage, reverse=True)
    top_sectors = sorted_sectors[:3]
    sector_str = ", ".join([f"{s.sector} ({s.percentage:.1f}%)" for s in top_sectors])
    
    return f"""Current Portfolio Status:
- Total Value: ${summary.total_value_usd:,.2f}
- Cost Basis: ${summary.total_cost_basis_usd:,.2f}
- Total Gain/Loss: ${summary.total_gain_loss_usd:,.2f} ({summary.total_gain_loss_pct:.2f}%)
- Daily Change: ${summary.daily_pnl_usd:,.2f} ({summary.daily_pnl_pct:.2f}%)
- Top Sectors: {sector_str if sector_str else 'N/A'}"""

async def get_user_context_data(db: AsyncSession, user_id: str) -> Dict[str, Any]:
    """
    Fetches the portfolio summary and raw holdings for a user.
    Returns a dictionary suitable for updating the AgentState.user_context.
    """
    summary = await get_portfolio_summary(db, user_id)
    formatted_summary = format_portfolio_for_llm(summary)
    
    # Fetch raw holdings with asset details
    stmt = (
        select(Holding)
        .options(selectinload(Holding.asset))
        .where(Holding.user_id == user_id, Holding.quantity_held > 0)
    )
    result = await db.execute(stmt)
    holdings_records = result.scalars().all()
    
    portfolio_data = []
    for h in holdings_records:
        asset = h.asset
        current_price = await get_current_price(db, asset)
        portfolio_data.append({
            "symbol": asset.symbol,
            "name": asset.name,
            "type": asset.type.value if hasattr(asset.type, "value") else str(asset.type),
            "sector": asset.sector or "Unknown",
            "quantity": float(h.quantity_held),
            "avg_cost_basis": float(h.avg_cost_basis),
            "current_price": float(current_price),
            "value": float(h.quantity_held * current_price),
            "return_pct": float(((current_price / h.avg_cost_basis) - 1) * 100) if h.avg_cost_basis > 0 else 0.0
        })
    
    return {
        "user_id": user_id,
        "portfolio_summary": formatted_summary,
        "portfolio": portfolio_data
    }
