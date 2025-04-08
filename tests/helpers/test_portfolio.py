"""Tests for helpers.portfolio."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
import pytest_asyncio

from pypmanager.database.market_data import AsyncMarketDataDB, MarketDataModel
from pypmanager.helpers.portfolio import (
    async_get_holding_by_isin,
    async_get_holdings,
)
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.conftest import DataFactory


@pytest_asyncio.fixture(name="async_market_data")
async def transaction_data_v2_fixture() -> Generator[None]:
    """Mock transactions by inserting into database."""
    sample_market_data = [
        MarketDataModel(
            isin_code="US1234567890",
            report_date=date(2021, 1, 1),
            close_price=100.0,
            currency=None,
            date_added=date(2023, 1, 2),
            source="test",
        )
    ]
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)


@pytest.fixture(name="transaction_data")
def transaction_data_fixture(
    data_factory: type[DataFactory],
) -> Generator[None]:
    """Fixture for transaction data."""
    factory = data_factory()

    mocked_transactions = (
        # US1234567890
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        )
        # US1234567891
        .buy(
            name="Company B",
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone),
            isin_code="US1234567891",
        )
        .sell(
            name="Company B",
            transaction_date=datetime(2021, 1, 2, tzinfo=Settings.system_time_zone),
            isin_code="US1234567891",
        )
        .df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_async_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        yield


@pytest.mark.asyncio
@pytest.mark.usefixtures("async_market_data")
@pytest.mark.usefixtures("transaction_data")
async def test_async_get_holdings() -> None:
    """Test async_get_holdings."""
    result = await async_get_holdings()
    # One security has been sold so there should only be one holding

    assert len(result) == 2

    assert result[0].name == "Company A"
    assert result[0].invested_amount == 100.0
    assert result[0].current_market_value_amount == 1000.0
    assert result[0].pnl_unrealized == 900.0
    assert result[0].pnl_trade == 0.0
    assert result[0].pnl_dividend == 0.0
    assert result[0].market_value_price == 100.0
    assert result[0].market_value_date == date(2021, 1, 1)
    assert result[0].cost_base_average == 10.0
    assert result[0].quantity_held == 10.0

    assert result[1].name == "Company B"
    assert result[1].invested_amount is None
    assert result[1].current_market_value_amount is None
    assert result[1].pnl_unrealized is None
    assert result[0].pnl_trade == 0.0
    assert result[0].pnl_dividend == 0.0
    assert result[1].market_value_price is None
    assert result[1].market_value_date is None
    assert result[1].cost_base_average is None
    assert result[1].quantity_held is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("async_market_data")
@pytest.mark.usefixtures("transaction_data")
async def test_async_get_holding_by_isin() -> None:
    """Test async_get_holding_by_isin."""
    result = await async_get_holding_by_isin(
        isin_code="US1234567890",
    )
    assert result.name == "Company A"
    assert result.invested_amount == 100.0
    assert result.current_market_value_amount == 1000.0
    assert result.pnl_unrealized == 900.0
    assert result.pnl_trade == 0.0
    assert result.pnl_dividend == 0.0
    assert result.market_value_price == 100.0
    assert result.market_value_date == date(2021, 1, 1)
    assert result.cost_base_average == 10.0
    assert result.quantity_held == 10.0


@pytest.mark.asyncio
@pytest.mark.usefixtures("transaction_data")
async def test_async_get_holding_by_isin__none() -> None:
    """Test async_get_holding_by_isin for None."""
    result = await async_get_holding_by_isin(isin_code="abc123")
    assert result is None
