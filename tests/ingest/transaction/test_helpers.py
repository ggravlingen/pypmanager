"""Test helpers."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.ingest.transaction.helpers import (
    async_aggregate_income_statement_by_year,
)
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


@pytest.mark.asyncio()
async def test_async_aggregate_ledger_by_year(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_aggregate_ledger_by_year."""
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
        df_income_statement = await async_aggregate_income_statement_by_year()
        assert df_income_statement.columns.to_list() == ["index", 2021, 2022]
        assert len(df_income_statement) == 3
