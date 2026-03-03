from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
import hashlib
import uuid
from contextvars import ContextVar
from typing import Generator, Optional

from src.database.models import User, UserStatus, RefreshToken
from src.schemas.auth import UserSignUp, UserSignIn
from src.config import settings
from src.database.session import get_db

# ContextVar for deep service propagation of user identity
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)

# Argon2id with recommended parameters for high security
# Memory: 64MB, Iterations: 3, Parallelism: 4 (RFC 9106)
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return ph.hash(password)

def verify_password(hashed: str, password: str) -> bool:
    """Verify a password against an Argon2id hash."""
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False
    except Exception:
        # Catch-all for any other verification issues (e.g. malformed hash)
        return False

def check_needs_rehash(hashed: str) -> bool:
    """Check if a hash needs rehashing (e.g. if parameters changed)."""
    return ph.check_needs_rehash(hashed)

def create_access_token(user_id: str) -> str:
    """Generate a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "type": "access",
        "iat": int(now.timestamp())
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def create_refresh_token(db: AsyncSession, user_id: str, user_agent: str = None) -> str:
    """Generate and persist a long-lived refresh token."""
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    # Store SHA-256 hash of the JTI in DB for secure lookup
    token_hash = hashlib.sha256(jti.encode()).hexdigest()
    
    # Database expects naive datetime for TIMESTAMP WITHOUT TIME ZONE
    db_expire = expire.replace(tzinfo=None)
    
    new_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        user_agent=user_agent,
        expires_at=db_expire,
        created_at=now.replace(tzinfo=None)
    )
    
    db.add(new_token)
    await db.commit()
    
    # Payload for the token itself contains the raw JTI and UTC timestamps
    to_encode = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp())
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def authenticate_user(db: AsyncSession, data: UserSignIn) -> User:
    """Validate user credentials and status."""
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(user.hashed_password, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Phase 10 Decision: Return 401 if not active (e.g. pending email verification)
    if user.status != UserStatus.ACTIVE:
        # Note: In a real app, we might give a more specific message like "Email not verified"
        # but the decision in 10-CONTEXT.md was "single generic error message".
        # However, for UX we might want to differentiate. For now, following 10-CONTEXT.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    return user

async def create_user(db: AsyncSession, data: UserSignUp) -> User:
    """Create a new user with email uniqueness check."""
    # Check for existing email
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    user_dict = data.model_dump()
    password = user_dict.pop("password")
    user_dict["hashed_password"] = hash_password(password)
    user_dict["status"] = UserStatus.ACTIVE # Set to ACTIVE immediately per user request
    
    # Ensure naive datetimes for standard fields if not handled by model defaults
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user_dict["created_at"] = now
    user_dict["updated_at"] = now
    
    new_user = User(**user_dict)
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    except Exception as e:
        await db.rollback()
        raise e

async def revoke_all_user_sessions(db: AsyncSession, user_id: str):
    """Delete all refresh tokens for a specific user (theft detection or manual revoke)."""
    query = delete(RefreshToken).where(RefreshToken.user_id == user_id)
    await db.execute(query)
    await db.commit()

async def revoke_refresh_token(db: AsyncSession, refresh_token: str):
    """Revoke a single refresh token by its jti hash."""
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            return
        token_hash = hashlib.sha256(jti.encode()).hexdigest()
        query = delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        await db.execute(query)
        await db.commit()
    except (jwt.PyJWTError, KeyError):
        # Already invalid or malformed, ignore
        pass

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/signin")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Dependency to get the current authenticated and active user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        token_type: str = payload.get("type")
        if token_type != "access":
            # Only access tokens are allowed for this dependency
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
        
    return user

async def set_user_context(user: User = Depends(get_current_user)) -> Generator[User, None, None]:
    """Sets the user_id ContextVar and yields the user object."""
    token = user_id_ctx.set(user.id)
    try:
        yield user
    finally:
        user_id_ctx.reset(token)

async def rotate_refresh_token(db: AsyncSession, refresh_token: str, user_agent: str) -> tuple[str, str]:
    """
    Implements Refresh Token Rotation with theft detection and grace period.
    Returns (new_access_token, new_refresh_token).
    """
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        jti = payload.get("jti")
        user_id = payload.get("sub")
        
        if not jti or not user_id:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
             
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    token_hash = hashlib.sha256(jti.encode()).hexdigest()
    
    # 1. Look up token in DB
    query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(query)
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        # Token not found - could be a reused token whose chain was already revoked,
        # or a fake but validly signed token. Revoke all for safety.
        await revoke_all_user_sessions(db, user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # 2. Check Expiry (even if JWT signature is valid, DB might have different info)
    if token_record.expires_at < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    # 3. Theft Detection & Grace Period
    if token_record.rotated_at:
        grace_period_end = token_record.rotated_at + timedelta(seconds=10)
        if now > grace_period_end:
            # Token reused after grace period -> Theft detected!
            await revoke_all_user_sessions(db, user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Security breach detected. All sessions revoked."
            )
        else:
            # Within grace period. 
            pass

    # 4. Perform Rotation
    new_access_token = create_access_token(user_id)
    
    # Generate new refresh token
    new_jti = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)
    new_expire_utc = now_utc + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_token_hash = hashlib.sha256(new_jti.encode()).hexdigest()
    
    # Update current token's rotated_at if not already set
    if not token_record.rotated_at:
        token_record.rotated_at = now
    
    # Create child token record
    new_refresh_token_record = RefreshToken(
        user_id=user_id,
        token_hash=new_token_hash,
        user_agent=user_agent,
        parent_token_id=token_record.id,
        expires_at=new_expire_utc.replace(tzinfo=None)
    )
    
    db.add(new_refresh_token_record)
    await db.commit()
    
    # Payload for the new token
    to_encode = {
        "sub": user_id,
        "exp": int(new_expire_utc.timestamp()),
        "jti": new_jti,
        "type": "refresh",
        "iat": int(now_utc.timestamp())
    }
    encoded_refresh_token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return new_access_token, encoded_refresh_token
