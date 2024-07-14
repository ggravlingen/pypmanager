"""Test helpers."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.general_ledger import async_aggregate_ledger_by_year


@pytest.fixture
def _mock_transactions_general_ledger(
    df_transaction_data_factory: Callable[[int], pd.DataFrame],
) -> Generator[None, Any, None]:
    """Mock the transaction list."""
    mocked_transactions = df_transaction_data_factory(no_rows=10)

    # make the transaction_date field into the index
    mocked_transactions.index = mocked_transactions["transaction_date"]

    with (
        patch(
            "pypmanager.general_ledger.helpers.load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        yield


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transactions_general_ledger")
async def test_async_aggregate_ledger_by_year() -> None:
    """Test function async_aggregate_ledger_by_year."""
    ledger = await async_aggregate_ledger_by_year()
    assert ledger.columns.to_list() == ["year", "ledger_account", "net"]
    assert len(ledger) == 1
