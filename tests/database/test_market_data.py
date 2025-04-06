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


@pytest.fixture(scope="session", autouse=True)
def _mock_settings() -> Generator[Any, Any, Any]:
    """Fixture for mocking settings."""
    with patch.object(
        TypedSettings, "database_local", new_callable=PropertyMock
    ) as mock:
        mock.return_value = Path("tests/test.sqllite").resolve()
        yield


@pytest.fixture(name="sample_market_data")
def _sample_market_data() -> list[MarketDataModel]:
    """Fixture providing sample market data for testing."""
    return [
        MarketDataModel(
            isin="US0378331005",  # Apple
            report_date=date(2023, 1, 1),
            close_price=150.25,
            currency=None,
            date_added=date(2023, 1, 2),
            source="test",
        ),
        MarketDataModel(
            isin="US0231351067",  # Amazon
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
        assert Path("tests/test.sqllite").exists()


@pytest.mark.asyncio
async def test_store_market_data(
    sample_market_data: list[MarketDataModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test inserting data into the table."""
    async with AsyncMarketDataDB() as db:
        await db.store_market_data(data=sample_market_data)
        assert "Stored 2 market data records" in caplog.text
