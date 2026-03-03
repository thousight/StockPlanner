from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, status
from src.database.models import User, UserStatus
from src.schemas.auth import UserSignUp

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
    user_dict["status"] = UserStatus.PENDING # Ensure PENDING status
    
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
