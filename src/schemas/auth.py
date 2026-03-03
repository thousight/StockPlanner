from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date, datetime
import re
from src.database.models import RiskTolerance, UserStatus

class UserSignUp(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    base_currency: str = Field("USD", min_length=3, max_length=3)
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    display_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    status: UserStatus
    risk_tolerance: RiskTolerance
    base_currency: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
