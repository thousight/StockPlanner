from fastapi import APIRouter, Depends, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.database.session import get_db
from src.database.models import User
from src.schemas.auth import UserSignUp, UserResponse, UserSignIn, TokenResponse, TokenRefreshRequest
from src.services.auth import (
    create_user, 
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    rotate_refresh_token,
    revoke_refresh_token,
    revoke_all_user_sessions,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return current_user

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserSignUp, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    """
    return await create_user(db, data)

@router.post("/signin", response_model=TokenResponse)
async def signin(
    data: UserSignIn, 
    request: Request,
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate and receive Access + Refresh tokens.
    """
    user = await authenticate_user(db, data)
    
    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(db, user.id, user_agent)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: TokenRefreshRequest,
    request: Request,
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange a valid refresh token for a new pair of tokens.
    """
    new_access, new_refresh = await rotate_refresh_token(db, data.refresh_token, user_agent)
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }

@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(
    data: TokenRefreshRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Invalidate a specific refresh token session.
    """
    await revoke_refresh_token(db, data.refresh_token)
    return None

@router.post("/revoke-all", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Invalidate all active sessions for the current user.
    """
    await revoke_all_user_sessions(db, current_user.id)
    return None
