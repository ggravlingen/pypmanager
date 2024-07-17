"""Test helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.general_ledger import async_aggregate_ledger_by_year

if TYPE_CHECKING:
    from tests.conftest import DataFactory


@pytest.mark.asyncio()
async def test_async_aggregate_ledger_by_year(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_aggregate_ledger_by_year."""
    factory = data_factory()
    mocked_transactions = factory.buy().sell().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        ledger = await async_aggregate_ledger_by_year()
        assert ledger.columns.to_list() == ["ledger_account", 2021]
        assert len(ledger) == 1
