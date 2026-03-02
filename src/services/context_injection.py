from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.portfolio import PortfolioSummary
from src.services.portfolio import get_portfolio_summary

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
    Fetches the portfolio summary for a user and returns a dictionary 
    suitable for updating the AgentState.user_context.
    """
    summary = await get_portfolio_summary(db, user_id)
    formatted_summary = format_portfolio_for_llm(summary)
    
    return {
        "user_id": user_id,
        "portfolio_summary": formatted_summary
    }
