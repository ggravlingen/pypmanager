"""Tests for pandas algorithm."""

from __future__ import annotations

import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import TransactionTypeValues
from pypmanager.ingest.transaction.pandas_algorithm import PandasAlgorithm


@pytest.mark.parametrize(
    ("trans_type", "no_traded", "expected"),
    [
        (TransactionTypeValues.BUY, 10, 10),
        (TransactionTypeValues.DIVIDEND, 15, 15),
        (TransactionTypeValues.SELL, -5, -5),
    ],
)
def test__normalize_no_traded(trans_type: str, no_traded: int, expected: int) -> None:
    """Test function _normalize_no_traded."""
    test_data = pd.DataFrame(
        {"transaction_type": [trans_type], "no_traded": [no_traded]},
    )
    result = PandasAlgorithm.normalize_no_traded(test_data.iloc[0])

    assert result == expected
