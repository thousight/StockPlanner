import pytest
from typing import AsyncGenerator, Optional
from httpx import AsyncClient, Response, ASGITransport
from unittest.mock import create_autospec
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from src.services.auth import create_access_token
from src.database.models import User, UserStatus, RiskTolerance

class TraceableAsyncClient(AsyncClient):
    """
    AsyncClient that stores the last response to extract Request IDs on failure.
    """
    last_response: Optional[Response] = None

    async def request(self, *args, **kwargs) -> Response:
        self.last_response = await super().request(*args, **kwargs)
        return self.last_response

@pytest.fixture
async def client() -> AsyncGenerator[TraceableAsyncClient, None]:
    """
    Provides a traceable httpx AsyncClient.
    """
    async with TraceableAsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
def mock_session():
    """
    Provides a mock SQLAlchemy AsyncSession.
    """
    return create_autospec(AsyncSession)

@pytest.fixture
def test_user():
    """Provides a consistent test user object."""
    return User(
        id="019cb265-1862-76d0-8ebb-10273b096f66",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        status=UserStatus.ACTIVE,
        risk_tolerance=RiskTolerance.MODERATE,
        base_currency="USD"
    )

@pytest.fixture
def auth_headers(test_user):
    """Provides auth headers for the primary test user."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to extract and print X-Request-ID on test failure.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Check if the test has a 'client' fixture
        if "client" in item.funcargs:
            client = item.funcargs["client"]
            if hasattr(client, "last_response") and client.last_response:
                # CorrelationIdMiddleware uses X-Request-ID by default
                request_id = client.last_response.headers.get("X-Request-ID")
                if request_id:
                    # Print with newline to ensure it's visible in pytest output
                    print(f"\n[FAILURE TRACE] X-Request-ID: {request_id}")
