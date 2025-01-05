"""Tests for helpers.income_statement."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.helpers.income_statement import (
    async_pnl_by_year,
    async_pnl_get_isin_map,
)
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


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
        # Company C
        .buy(
            name="Company C",
            isin_code="US1234567893",
            transaction_date=datetime(2021, 1, 3, tzinfo=Settings.system_time_zone),
        )
        .dividend(
            name="Company C",
            isin_code="US1234567893",
        )
        .df_transaction_list
    )

    with patch(
        "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
        "_load_transaction_files",
        return_value=mocked_transactions,
    ):
        df_transaction_registry_all = await TransactionRegistry().async_get_registry()

        result = await async_pnl_get_isin_map(
            df_transaction_registry_all=df_transaction_registry_all
        )

        assert result.get("US1234567890").pnl_total == 49.0
        assert result.get("US1234567890").pnl_trade == 49.0
        assert result.get("US1234567890").pnl_dividend == 0

        assert result.get("US1234567891").pnl_total == -101.0
        assert result.get("US1234567891").pnl_trade == -101.0
        assert result.get("US1234567891").pnl_dividend == 0

        assert result.get("US1234567892") is None

        assert result.get("US1234567893").pnl_total == 150.0
        assert result.get("US1234567893").pnl_trade == 0
        assert result.get("US1234567893").pnl_dividend == 150.0


@pytest.mark.asyncio
async def test_async_pnl_by_year(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_pnl_by_year."""
    factory = data_factory()
    mocked_transactions = (
        factory.buy()
        .sell()
        .dividend(
            transaction_date=datetime(
                2022,
                2,
                1,
                tzinfo=Settings.system_time_zone,
            ),
        )
        .df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        income_statement_list = await async_pnl_by_year()

        assert income_statement_list[0].year_list == [2021, 2022]
        assert income_statement_list[0].item_name == "calc_pnl_transaction_dividend"
        assert income_statement_list[0].amount_list == [None, 150.0]
        assert income_statement_list[0].is_total is False

        assert income_statement_list[1].year_list == [2021, 2022]
        assert income_statement_list[1].item_name == "calc_pnl_transaction_trade"
        assert income_statement_list[1].amount_list == [49.0, None]
        assert income_statement_list[1].is_total is False

        assert income_statement_list[2].year_list == [2021, 2022]
        assert income_statement_list[2].item_name == "calc_pnl_transaction_total"
        assert income_statement_list[2].amount_list == [49.0, 150.0]
        assert income_statement_list[2].is_total is True
