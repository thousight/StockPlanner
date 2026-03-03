import pytest
from unittest.mock import AsyncMock, patch
from decimal import Decimal
from src.schemas.portfolio import PortfolioSummary, SectorAllocation, BenchmarkComparison
from main import app
from src.database.session import get_db

@pytest.mark.asyncio
async def test_get_portfolio_summary(client, mock_session):
    """
    Test GET /investment (Portfolio Analytics).
    Verify JSON structure and numeric precision.
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

    # Dependency override
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.portfolio.get_portfolio_summary", new_callable=AsyncMock) as mock_get_summary:
        mock_get_summary.return_value = mock_summary
        
        response = await client.get(
            "/investment",
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_value_usd"] == "10000.00"
        assert data["total_gain_loss_pct"] == "0.25"
        assert len(data["sector_allocation"]) == 2
        assert data["benchmark"]["benchmark_name"] == "SPY"
        
        mock_get_summary.assert_called_once_with(mock_session, "user123")

    # Clean up
    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_get_portfolio_summary_missing_header(client):
    """
    Test GET /investment without X-User-ID header.
    Should return 422 Unprocessable Entity.
    """
    response = await client.get("/investment")
    assert response.status_code == 422
    assert "X-User-ID" in response.text

@pytest.mark.asyncio
async def test_get_portfolio_summary_error(client, mock_session):
    """
    Test GET /investment when service layer raises an exception.
    """
    # Dependency override
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.portfolio.get_portfolio_summary", new_callable=AsyncMock) as mock_get_summary:
        mock_get_summary.side_effect = Exception("Service error")
        
        response = await client.get(
            "/investment",
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]

    # Clean up
    del app.dependency_overrides[get_db]
