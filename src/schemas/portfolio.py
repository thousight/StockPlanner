from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional, Dict

class SectorAllocation(BaseModel):
    sector: str
    value_usd: Decimal
    percentage: Decimal

class BenchmarkComparison(BaseModel):
    benchmark_name: str
    portfolio_gain_pct: Decimal
    benchmark_gain_pct: Decimal
    relative_performance: Decimal

class PortfolioSummary(BaseModel):
    total_value_usd: Decimal
    total_cost_basis_usd: Decimal
    total_gain_loss_usd: Decimal
    total_gain_loss_pct: Decimal
    daily_pnl_usd: Decimal
    daily_pnl_pct: Decimal
    sector_allocation: List[SectorAllocation]
    benchmark: Optional[BenchmarkComparison] = None
