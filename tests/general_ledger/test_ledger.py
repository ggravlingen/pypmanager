"""Tests for the general ledger."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypmanager.general_ledger import GeneralLedger

if TYPE_CHECKING:
    from tests.conftest import DataFactory


def test_class_general_ledger(
    data_factory: DataFactory,
) -> None:
    """Test functionality of GeneralLedger."""
    mocked_transactions = data_factory.buy().df_transaction_list
    ledger = GeneralLedger(transactions=mocked_transactions)

    assert len(ledger.transactions) == 1
