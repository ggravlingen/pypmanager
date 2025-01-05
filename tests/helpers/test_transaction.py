"""Tests for helpers.transaction."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.helpers.transaction import async_get_all_transactions
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


@pytest.mark.asyncio
async def test_async_get_all_transactions(
    data_factory: type[DataFactory],
) -> None:
    """Test async_get_all_transactions."""
    factory = data_factory()
    mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2022, 11, 1, tzinfo=Settings.system_time_zone)
        )
        .sell(transaction_date=datetime(2022, 11, 2, tzinfo=Settings.system_time_zone))
        .df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        result = await async_get_all_transactions()
        assert result[0].transaction_date == datetime(
            2022, 11, 2, tzinfo=Settings.system_time_zone
        )
        assert result[0].broker == "Broker A"
        assert result[0].action == "Sell"
        assert result[0].name == "Company A"
        assert result[0].no_traded == 10.0
        assert result[0].commission == -1.0
        assert result[0].fx == 1.0
        assert result[0].isin_code == "US1234567890"
        assert result[0].price == 15.0
        assert result[0].currency == "SEK"
        assert result[0].cash_flow == 149.0
        assert result[0].cost_base_average is None
        assert result[0].pnl_total == 49.0
        assert result[0].pnl_trade == 49.0
        assert result[0].pnl_dividend is None
        assert result[0].quantity_held is None

        assert result[1].transaction_date == datetime(
            2022, 11, 1, tzinfo=Settings.system_time_zone
        )
        assert result[1].broker == "Broker A"
        assert result[1].action == "Buy"
        assert result[1].name == "Company A"
        assert result[1].no_traded == 10.0
        assert result[1].commission == -1.0
        assert result[1].fx == 1.0
        assert result[1].isin_code == "US1234567890"
        assert result[1].price == 10.0
        assert result[1].currency == "SEK"
        assert result[1].cash_flow == -101.0
        assert result[1].cost_base_average == 10.0
        assert result[1].pnl_total == 0.0
        assert result[1].pnl_trade is None
        assert result[1].pnl_dividend is None
        assert result[1].quantity_held == 10.0
