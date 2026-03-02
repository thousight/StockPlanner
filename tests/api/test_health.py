import pytest
from httpx import AsyncClient

async def test_health_check(client: AsyncClient):
    """
    Verifies that the health check endpoint returns 200 OK.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

async def test_root(client: AsyncClient):
    """
    Verifies that the root endpoint returns 200 OK.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "StockPlanner" in response.json()["message"]

async def test_failure_hook_behavior(client: AsyncClient):
    """
    A test intended to fail to manually verify that X-Request-ID is printed.
    Uncomment the assertion to test the hook.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    # assert response.status_code == 404, "Forcing failure to check Request ID hook"
