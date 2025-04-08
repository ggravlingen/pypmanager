"""Tests for database.market_data module."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from pypmanager.database.market_data import (
    AsyncMarketDataDB,
    MarketDataModel,
)

from tests.conftest import DB_NAME_TEST


@pytest.mark.asyncio
async def test_create_database() -> None:
    """Test the creation of the database."""
    async with AsyncMarketDataDB():
        assert Path("tests") / DB_NAME_TEST


@pytest.mark.asyncio
async def test_store_market_data(
    sample_market_data: list[MarketDataModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test inserting data into the table."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)
        assert "Stored 2 market data records" in caplog.text


@pytest.mark.asyncio
async def test_get_market_data(
    sample_market_data: list[MarketDataModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test method get_market_data."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)
        assert "Stored 2 market data records" in caplog.text

        data = await db.async_get_market_data(
            isin_code="US0378331005",
            report_date=date(2023, 1, 1),
        )

        assert data is not None
        assert data.isin_code == "US0378331005"
        assert data.close_price == 150.25
        assert data.report_date == date(2023, 1, 1)
        assert data.source == "test"


@pytest.mark.asyncio
async def test_get_market_data__none() -> None:
    """Test method get_market_data for None return."""
    async with AsyncMarketDataDB() as db:
        data = await db.async_get_market_data(
            isin_code="abc123",
            report_date=date(2023, 1, 1),
        )
        assert data is None


@pytest.mark.asyncio
async def test_async_get_last_close_price_by_isin(
    sample_market_data: list[MarketDataModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test method async_get_last_close_price_by_isin."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)
        assert "Stored 2 market data records" in caplog.text

        data = await db.async_get_last_close_price_by_isin()

        assert data == [
            ("US0231351067", "2023-01-01", 102.75),
            ("US0378331005", "2023-01-01", 150.25),
        ]
        assert len(data) == 2
