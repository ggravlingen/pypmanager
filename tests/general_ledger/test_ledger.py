"""Tests for the general ledger."""

from collections.abc import Callable

import pandas as pd

from pypmanager.general_ledger import GeneralLedger


def test_class_general_ledger(
    df_transaction_data_factory: Callable[[int], pd.DataFrame],
) -> None:
    """Test functionality of GeneralLedger."""
    fixture_df_transaction_data = df_transaction_data_factory(no_rows=1)

    ledger = GeneralLedger(transactions=fixture_df_transaction_data)

    assert len(ledger.transactions) == 1
