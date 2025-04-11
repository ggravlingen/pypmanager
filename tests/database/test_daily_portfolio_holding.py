"""Tests for database.market_data module."""

from __future__ import annotations

import pytest

from pypmanager.database.daily_portfolio_holding import (
    AsyncDbDailyPortfolioHolding,
    DailyPortfolioMoldingModel,
)


@pytest.mark.asyncio
async def test_async_store_data(
    sample_daily_portfolio_holding: list[DailyPortfolioMoldingModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test inserting data into the table."""
    async with AsyncDbDailyPortfolioHolding() as db:
        await db.async_store_data(data=sample_daily_portfolio_holding)
        assert "Committed 1 items (skipped 0)" in caplog.text


@pytest.mark.asyncio
async def test_async_get_all_data(
    sample_daily_portfolio_holding: list[DailyPortfolioMoldingModel],
) -> None:
    """Test method get_market_data."""
    async with AsyncDbDailyPortfolioHolding() as db:
        await db.async_store_data(data=sample_daily_portfolio_holding)
        data = await db.async_filter_all()
        assert len(data) == 1

        assert data[0].isin_code == "US0378331005"
        assert data[0].report_date == "2023-01-01"
        assert data[0].no_held == 10.0
