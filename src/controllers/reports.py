from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database.session import get_db
from src.database.models import Report as ReportModel, ReportCategory
from src.schemas.reports import ReportList
from typing import Optional

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("", response_model=ReportList)
async def get_reports(
    q: Optional[str] = Query(None),
    category: Optional[ReportCategory] = Query(None),
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    query = select(ReportModel).where(ReportModel.user_id == x_user_id)
    if category:
        query = query.where(ReportModel.category == category)
    if q:
        ts_query = func.websearch_to_tsquery('english', q)
        query = query.where(ReportModel.search_vector.op('@@')(ts_query))
        query = query.order_by(func.ts_rank_cd(ReportModel.search_vector, ts_query).desc())
    else:
        query = query.order_by(ReportModel.created_at.desc())
    result = await db.execute(query)
    reports = result.scalars().all()
    return {"reports": reports, "total": len(reports)}
