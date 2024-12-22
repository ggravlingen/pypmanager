"""Tests for chart helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.helpers.chart import async_get_market_data_and_transaction
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


@pytest.mark.asyncio
async def test_async_get_market_data_and_transaction(
    data_factory: type[DataFactory],
) -> None:
    """Test async_get_market_data_and_transaction."""
    factory = data_factory()
    mocked_transactions = factory.buy(
        transaction_date=datetime(2022, 11, 2, tzinfo=Settings.system_time_zone)
    ).df_transaction_list
    with (
        patch(
            "pypmanager.helpers.chart.TransactionRegistry._load_transaction_files",
            return_value=mocked_transactions,
        ),
        patch(
            "pypmanager.helpers.chart.get_market_data",
        ) as mock_get_market_data,
    ):
        mock_get_market_data.return_value = pd.DataFrame(
            [
                {
                    "isin_code": "US1234567890",
                    "name": "Test",
                    "report_date": date(2022, 11, 1),
                    "price": 100.0,
                    "date_added_utc": datetime(2022, 11, 1, tzinfo=UTC),
                    "source": "test",
                },
                {
                    "isin_code": "US1234567890",
                    "name": "Test",
                    "report_date": date(2022, 11, 2),
                    "price": 99.0,
                    "date_added_utc": datetime(2022, 11, 1, tzinfo=UTC),
                    "source": "test",
                },
            ]
        ).set_index("report_date")
        result = await async_get_market_data_and_transaction(
            isin_code="US1234567890",
            start_date=date(2022, 11, 1),
            end_date=date(2022, 11, 30),
        )

        assert len(result) == 22
