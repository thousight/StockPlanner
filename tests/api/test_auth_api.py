import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from src.database.session import get_db
from src.database.models import User, UserStatus, RefreshToken, RiskTolerance
from src.services.auth import hash_password, create_access_token, create_refresh_token
from unittest.mock import AsyncMock, MagicMock, patch
import jwt
import hashlib
from src.config import settings
from datetime import datetime, timedelta, timezone
from uuid import uuid4

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock() # Sync method
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()
    return db

def create_mock_user(user_id="user-123", email="test@example.com", status=UserStatus.ACTIVE):
    return User(
        id=user_id,
        email=email,
        hashed_password=hash_password("StrongPass123!"),
        first_name="Test",
        last_name="User",
        status=status,
        risk_tolerance=RiskTolerance.MODERATE,
        base_currency="USD",
        timezone="UTC",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_signup_success(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    def side_effect_add(user):
        user.id = str(uuid4())
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.timezone = "UTC"
        return None

    mock_db.add.side_effect = side_effect_add
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    payload = {
        "email": "NEW@example.com",
        "password": "StrongPass123!",
        "first_name": "John",
        "last_name": "Doe",
        "risk_tolerance": "MODERATE",
        "base_currency": "USD"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/signup", json=payload)
        
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["status"] == "ACTIVE"
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_signup_validation_weak_password():
    payload = {
        "email": "test@example.com",
        "password": "weak",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/signup", json=payload)
        
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_signup_duplicate_email(mock_db):
    mock_user = create_mock_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    payload = {
        "email": "test@example.com",
        "password": "StrongPass123!",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/signup", json=payload)
        
    assert response.status_code == 409
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_signin_success(mock_db, client):
    mock_user = create_mock_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # OAuth2PasswordRequestForm expects form data (username/password)
    payload = {"username": "test@example.com", "password": "StrongPass123!"}
    response = await client.post("/auth/signin", data=payload)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    mock_db.add.assert_called_once()
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_me_success(mock_db, client):
    mock_user = create_mock_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    token = create_access_token(mock_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == mock_user.email
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_refresh_token_success(mock_db, client):
    user_id = "user-123"
    refresh_token = await create_refresh_token(mock_db, user_id)
    
    payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    jti = payload["jti"]
    token_hash = hashlib.sha256(jti.encode()).hexdigest()
    
    mock_record = RefreshToken(
        id="token-id",
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10),
        rotated_at=None
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_record
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert mock_record.rotated_at is not None
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_refresh_token_theft_detection(mock_db, client):
    user_id = "user-123"
    refresh_token = await create_refresh_token(mock_db, user_id)
    
    payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    jti = payload["jti"]
    token_hash = hashlib.sha256(jti.encode()).hexdigest()
    
    mock_record = RefreshToken(
        id="token-id",
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10),
        rotated_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=11)
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_record
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    
    assert response.status_code == 401
    assert "Security breach" in response.json()["detail"]
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_signout_success(mock_db, client):
    mock_user = create_mock_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    token = create_access_token(mock_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.post("/auth/signout", json={"refresh_token": "dummy"}, headers=headers)
    
    assert response.status_code == 204
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_revoke_all_success(mock_db, client):
    mock_user = create_mock_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    token = create_access_token(mock_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.post("/auth/revoke-all", headers=headers)
    
    assert response.status_code == 204
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_inactive_user_rejection(mock_db, client):
    mock_user = create_mock_user(status=UserStatus.PENDING)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    token = create_access_token(mock_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/auth/me", headers=headers)
    
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"]
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_current_user_invalid_payload(client):
    # Token missing 'sub'
    payload = {"type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_wrong_token_type(client):
    # Refresh token used where access token expected
    payload = {"sub": "user-123", "type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_malformed_token(client):
    headers = {"Authorization": "Bearer not-a-token"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_rotate_invalid_token_type(client):
    # Access token used where refresh token expected
    payload = {"sub": "user-123", "type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    response = await client.post("/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 401
    assert "type" in response.json()["detail"]

@pytest.mark.asyncio
async def test_rotate_expired_refresh_token(client):
    payload = {
        "sub": "user-123", 
        "jti": "some-jti",
        "type": "refresh", 
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    response = await client.post("/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

def test_check_needs_rehash():
    from src.services.auth import check_needs_rehash
    pw = "Pass123!"
    hashed = hash_password(pw)
    assert check_needs_rehash(hashed) is False
