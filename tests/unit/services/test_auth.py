import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.services.auth import hash_password, verify_password, create_user
from src.schemas.auth import UserSignUp
from src.database.models import User, UserStatus

def test_hash_password_different_for_same_input():
    pw = "StrongPass123!"
    hash1 = hash_password(pw)
    hash2 = hash_password(pw)
    assert hash1 != hash2
    assert hash1.startswith("$argon2id$")

def test_verify_password_success():
    pw = "StrongPass123!"
    hashed = hash_password(pw)
    assert verify_password(hashed, pw) is True

def test_verify_password_mismatch():
    pw = "StrongPass123!"
    hashed = hash_password(pw)
    assert verify_password(hashed, "WrongPass123!") is False

def test_verify_password_malformed():
    assert verify_password("not-a-hash", "password") is False

@pytest.mark.asyncio
async def test_create_user_success(mock_session):
    # Setup
    data = UserSignUp(
        email="test@example.com",
        password="StrongPass123!",
        first_name="Test",
        last_name="User"
    )
    
    # Mock existing user check (None found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    # Execute
    user = await create_user(mock_session, data)
    
    # Verify
    assert user.email == "test@example.com"
    assert verify_password(user.hashed_password, "StrongPass123!") is True
    assert user.status == UserStatus.PENDING
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_duplicate_email(mock_session):
    # Setup
    data = UserSignUp(
        email="existing@example.com",
        password="StrongPass123!",
        first_name="Test",
        last_name="User"
    )
    
    # Mock existing user check (Found one)
    mock_user = User(email="existing@example.com")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Execute and Verify
    with pytest.raises(HTTPException) as excinfo:
        await create_user(mock_session, data)
    
    assert excinfo.value.status_code == 409
    assert "Email already registered" in excinfo.value.detail
    mock_session.add.assert_not_called()

@pytest.mark.asyncio
async def test_create_user_integrity_error(mock_session):
    # Setup
    data = UserSignUp(
        email="test@example.com",
        password="StrongPass123!",
        first_name="Test",
        last_name="User"
    )
    
    # Mock existing user check (None found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock IntegrityError on commit
    from sqlalchemy.exc import IntegrityError
    mock_session.commit = AsyncMock(side_effect=IntegrityError("duplicate", params={}, orig=None))
    mock_session.rollback = AsyncMock()
    
    # Execute and Verify
    with pytest.raises(HTTPException) as excinfo:
        await create_user(mock_session, data)
        
    assert excinfo.value.status_code == 409
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_general_exception(mock_session):
    # Setup
    data = UserSignUp(
        email="test@example.com",
        password="StrongPass123!",
        first_name="Test",
        last_name="User"
    )
    
    # Mock existing user check (None found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock General Error on commit
    mock_session.commit = AsyncMock(side_effect=Exception("Database down"))
    mock_session.rollback = AsyncMock()
    
    # Execute and Verify
    with pytest.raises(Exception) as excinfo:
        await create_user(mock_session, data)
        
    assert "Database down" in str(excinfo.value)
    mock_session.rollback.assert_called_once()
