"""Test helpers."""

from unittest.mock import patch

import pytest

from pypmanager.ingest.transaction.helpers import TransactionRegistry

from tests.conftest import DataFactory


@pytest.mark.asyncio()
async def test_transaction_registry(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_aggregate_ledger_by_year."""
    factory = data_factory()
    mocked_transactions = factory.buy().sell().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.helpers.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        registry = await TransactionRegistry().async_get_registry()
        assert len(registry) == 2
