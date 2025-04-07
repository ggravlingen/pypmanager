"""Tests for database.market_data module."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import PropertyMock, patch

import pytest

from pypmanager.database.market_data import (
    AsyncMarketDataDB,
    MarketDataModel,
)
from pypmanager.settings import TypedSettings

if TYPE_CHECKING:
    from collections.abc import Generator

DB_NAME_TEST = "test_database.sqllite"


@pytest.fixture(scope="session", autouse=True)
def _mock_settings() -> Generator[Any, Any, Any]:
    """Fixture for mocking settings."""
    db_path = Path("tests") / DB_NAME_TEST

    with patch.object(
        TypedSettings,
        "database_local",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = db_path

        yield

        # Cleanup after tests
        db_path.unlink(missing_ok=True)


@pytest.fixture(name="sample_market_data")
def _sample_market_data() -> list[MarketDataModel]:
    """Fixture providing sample market data for testing."""
    return [
        MarketDataModel(
            isin_code="US0378331005",  # Apple
            report_date=date(2023, 1, 1),
            close_price=150.25,
            currency=None,
            date_added=date(2023, 1, 2),
            source="test",
        ),
        MarketDataModel(
            isin_code="US0231351067",  # Amazon
            report_date=date(2023, 1, 1),
            close_price=102.75,
            currency=None,
            date_added=date(2023, 1, 2),
            source="test",
        ),
    ]


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
