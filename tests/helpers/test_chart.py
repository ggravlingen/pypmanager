"""Tests for chart helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.database.market_data import AsyncMarketDataDB, MarketDataModel
from pypmanager.helpers.chart import ChartData, async_get_market_data_and_transaction
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


def test_dataclass__chart_data__is_buy() -> None:
    """Test ChartData.is_buy."""
    chart_data = ChartData(
        x_val=date(2022, 11, 1),
        y_val=100.0,
        volume_buy=100.0,
        volume_sell=None,
        dividend_per_security=None,
    )

    assert chart_data.is_buy is True


def test_dataclass__chart_data__is_sell() -> None:
    """Test ChartData.is_sell."""
    chart_data = ChartData(
        x_val=date(2022, 11, 1),
        y_val=100.0,
        volume_buy=None,
        volume_sell=100.0,
        dividend_per_security=None,
    )

    assert chart_data.is_sell is True


@pytest.mark.asyncio
async def test_async_get_market_data_and_transaction(
    data_factory: type[DataFactory],
    sample_market_data: list[MarketDataModel],
) -> None:
    """Test async_get_market_data_and_transaction."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)

    factory = data_factory()
    mocked_transactions = factory.buy(
        isin_code="US0378331005",
        transaction_date=datetime(2022, 11, 2, tzinfo=Settings.system_time_zone),
    ).df_transaction_list

    with (
        patch(
            "pypmanager.helpers.chart.TransactionRegistry._async_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        result = await async_get_market_data_and_transaction(
            isin_code="US0378331005",
            start_date=date(2022, 11, 1),
            end_date=date(2022, 11, 30),
        )

        assert len(result) == 22
