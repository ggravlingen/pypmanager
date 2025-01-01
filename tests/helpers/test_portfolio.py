"""Tests for helpers.portfolio."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import numpy as np
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
    ):
        result = await async_async_get_holdings_v2()
        # One security has been sold so there should only be one holding
        assert len(result) == 2

        assert result[0].name == "Company A"
        assert result[0].invested_amount == 100.0
        assert result[0].current_market_value_amount == 0.0
        assert result[0].pnl_unrealized == 0.0
        assert result[0].date_market_value is None

        assert result[1].name == "Company B"
        assert np.isnan(result[1].invested_amount)
        assert result[1].current_market_value_amount == 0.0
        assert result[1].pnl_unrealized == 0.0
        assert result[1].date_market_value is None
