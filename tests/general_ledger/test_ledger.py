"""Tests for the general ledger."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.general_ledger import GeneralLedger
from pypmanager.ingest.transaction import TransactionRegistry

if TYPE_CHECKING:
    from tests.conftest import DataFactory


@pytest.mark.asyncio
async def test_class_general_ledger(
    data_factory: type[DataFactory],
) -> None:
    """Test functionality of GeneralLedger."""
    factory = data_factory()
    mocked_transactions = factory.buy().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        registry = await TransactionRegistry().async_get_registry()
        ledger = GeneralLedger(transactions=registry)

        assert len(ledger.transactions) == 1
