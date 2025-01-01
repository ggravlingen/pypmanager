"""Tests for helpers.portfolio."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.helpers.portfolio import async_async_get_holdings_v2
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


@pytest.mark.asyncio
async def test_async_async_get_holdings_v2(
    data_factory: type[DataFactory],
) -> None:
    """Test async_async_get_holdings_v2."""
    factory = data_factory()
    mocked_transactions = (
        # US1234567890
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        ).df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        result = await async_async_get_holdings_v2()
        assert len(result) == 1
        assert result[0].name == "Company A"
        assert result[0].invested_amount == 100.0
        assert result[0].current_market_value_amount == 0.0
