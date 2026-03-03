from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ReportCategory(str, Enum):
    STOCK = "STOCK"
    REAL_ESTATE = "REAL_ESTATE"
    MACRO = "MACRO"
    FUND = "FUND"
    GENERAL = "GENERAL"

class Report(BaseModel):
    id: int
    user_id: str
    thread_id: str
    title: str
    topic: str
    symbol: Optional[str] = None
    category: ReportCategory
    tags: Optional[Dict[str, Any]] = None
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportList(BaseModel):
    reports: List[Report]
    total: int
