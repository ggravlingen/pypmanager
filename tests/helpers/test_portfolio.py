"""Tests for helpers.portfolio."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.helpers.portfolio import async_async_get_holdings_v2, async_get_pnl_map
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory, MarketDataFactory


@pytest.mark.asyncio
async def test_async_async_get_holdings_v2(
    data_factory: type[DataFactory],
    market_data_factory: type[MarketDataFactory],
) -> None:
    """Test async_async_get_holdings_v2."""
    factory = data_factory()
    mocked_market_data = (
        market_data_factory().add(
            isin_code="US1234567890", report_date=date(2021, 1, 1), price=100.0
        )
    ).df_market_data_list

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
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
        patch(
            "pypmanager.helpers.market_data.get_market_data",
            return_value=mocked_market_data,
        ),
    ):
        result = await async_async_get_holdings_v2()
        # One security has been sold so there should only be one holding
        assert len(result) == 2

        assert result[0].name == "Company A"
        assert result[0].invested_amount == 100.0
        assert result[0].current_market_value_amount == 1000.0
        assert result[0].pnl_unrealized == 900.0
        assert result[0].pnl_realized == 0.0
        assert result[0].market_value_price == 100.0
        assert result[0].market_value_date == date(2021, 1, 1)
        assert result[0].cost_base_average == 10.0
        assert result[0].quantity_held == 10.0

        assert result[1].name == "Company B"
        assert result[1].invested_amount is None
        assert result[1].current_market_value_amount is None
        assert result[1].pnl_unrealized is None
        assert result[0].pnl_realized == 0.0
        assert result[1].market_value_price is None
        assert result[1].market_value_date is None
        assert result[1].cost_base_average is None
        assert result[1].quantity_held is None


@pytest.mark.asyncio
async def test_async_get_pnl(
    data_factory: type[DataFactory],
) -> None:
    """Test async_get_pnl."""
    factory = data_factory()
    mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        )
        .sell(
            transaction_date=datetime(2021, 1, 2, tzinfo=Settings.system_time_zone),
        )
        # Company B
        .buy(
            name="Company B",
            isin_code="US1234567891",
            transaction_date=datetime(2021, 1, 3, tzinfo=Settings.system_time_zone),
        )
        .sell(
            name="Company B",
            isin_code="US1234567891",
            transaction_date=datetime(2021, 1, 4, tzinfo=Settings.system_time_zone),
            price=0.0,
        )
        .df_transaction_list
    )

    with patch(
        "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
        "_load_transaction_files",
        return_value=mocked_transactions,
    ):
        df_transaction_registry = await TransactionRegistry().async_get_registry()

        result = await async_get_pnl_map(
            df_transaction_registry=df_transaction_registry
        )

        assert result.get("US1234567890") == 49.0
        assert result.get("US1234567891") == -101.0
        assert result.get("US1234567892") is None
