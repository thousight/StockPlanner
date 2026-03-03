import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from src.schemas.portfolio import PortfolioSummary, SectorAllocation, BenchmarkComparison
from main import app
from src.database.session import get_db
from src.database.models import User

@pytest.mark.asyncio
async def test_get_portfolio_summary(client, mock_session, auth_headers, test_user):
    """
    Test GET /investment (Portfolio Analytics).
    Verify JWT context and numeric precision.
    """
    # Setup mock return value
    mock_summary = PortfolioSummary(
        total_value_usd=Decimal("10000.00"),
        total_cost_basis_usd=Decimal("8000.00"),
        total_gain_loss_usd=Decimal("2000.00"),
        total_gain_loss_pct=Decimal("0.25"),
        daily_pnl_usd=Decimal("100.00"),
        daily_pnl_pct=Decimal("0.01"),
        sector_allocation=[
            SectorAllocation(sector="Technology", value_usd=Decimal("5000.00"), percentage=Decimal("0.5")),
            SectorAllocation(sector="Finance", value_usd=Decimal("5000.00"), percentage=Decimal("0.5")),
        ],
        benchmark=BenchmarkComparison(
            benchmark_name="SPY",
            portfolio_gain_pct=Decimal("0.25"),
            benchmark_gain_pct=Decimal("0.10"),
            relative_performance=Decimal("0.15")
        )
    )

    # Mock user lookup for auth dependency
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.portfolio.get_portfolio_summary", new_callable=AsyncMock) as mock_get_summary:
        mock_get_summary.return_value = mock_summary
        
        response = await client.get(
            "/investment",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_value_usd"] == "10000.00"
        assert data["total_gain_loss_pct"] == "0.25"
        
        # Verify it was called with test_user.id
        mock_get_summary.assert_called_once_with(mock_session, test_user.id)

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_get_portfolio_summary_unauthorized(client):
    """
    Test GET /investment without JWT.
    Should return 401 Unauthorized.
    """
    response = await client.get("/investment")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_portfolio_summary_error(client, mock_session, auth_headers, test_user):
    """
    Test GET /investment when service layer raises an exception.
    """
    # Mock user lookup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.portfolio.get_portfolio_summary", new_callable=AsyncMock) as mock_get_summary:
        mock_get_summary.side_effect = Exception("Service error")
        
        response = await client.get(
            "/investment",
            headers=auth_headers
        )
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]

    del app.dependency_overrides[get_db]
