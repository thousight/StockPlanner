from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.schemas.auth import UserSignUp, UserResponse
from src.services.auth import create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserSignUp, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    """
    return await create_user(db, data)
