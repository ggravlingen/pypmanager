"""Tests for database.market_data module."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from pypmanager.database.market_data import (
    AsyncMarketDataDB,
    MarketDataModel,
)
from pypmanager.helpers.market_data import async_sync_csv_to_db

from tests.conftest import DB_NAME_TEST


def test_model(sample_market_data: list[MarketDataModel]) -> None:
    """Test the MarketDataModel."""
    assert sample_market_data[0].isin_code == "US0378331005"
    assert sample_market_data[0].report_date == date(2023, 1, 1)
    assert sample_market_data[0].close_price == 150.25
    assert sample_market_data[0].currency is None
    assert sample_market_data[0].date_added == date(2023, 1, 2)
    assert sample_market_data[0].source == "test"
    assert str(sample_market_data[0]) == (
        "<MarketDataModel(isin_code=US0378331005, report_date=2023-01-01, "
        "close_price=150.25)>"
    )


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
        assert "Committed 2 items (skipped 0)" in caplog.text


@pytest.mark.asyncio
async def test_get_market_data(
    sample_market_data: list[MarketDataModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test method get_market_data."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)
        assert "Committed 2 items (skipped 0)" in caplog.text

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
        assert "Committed 2 items (skipped 0)" in caplog.text

        data = await db.async_get_last_close_price_by_isin()

        assert data == [
            ("US0231351067", "2023-01-01", 102.75),
            ("US0378331005", "2023-01-01", 150.25),
        ]
        assert len(data) == 2


@pytest.mark.asyncio
async def test_async_get_all_data(
    sample_market_data: list[MarketDataModel],
) -> None:
    """Test method get_market_data."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)
        data = await db.async_filter_all()
        assert len(data) == 2

        assert data[0].isin_code == "US0378331005"
        assert data[0].close_price == 150.25
        assert data[0].report_date == "2023-01-01"
        assert data[0].source == "test"


@pytest.mark.asyncio
async def test_async_sync_csv_to_db(caplog: pytest.LogCaptureFixture) -> None:
    """Test method async_sync_csv_to_db."""
    await async_sync_csv_to_db()
    assert "Stored 1 records from CSV files to the database" in caplog.text
