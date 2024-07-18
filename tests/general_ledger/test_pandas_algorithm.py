"""Tests for pandas algorithm."""

from __future__ import annotations

import pandas as pd
import pytest

from pypmanager.general_ledger.pandas_algorithm import PandasAlgorithmGeneralLedger
from pypmanager.ingest.transaction.const import ColumnNameValues


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        (
            pd.DataFrame(
                {
                    ColumnNameValues.CREDIT.value: [10.0],
                    ColumnNameValues.DEBIT.value: [None],
                }
            ),
            10.0,
        ),
        (
            pd.DataFrame(
                {
                    ColumnNameValues.CREDIT.value: [None],
                    ColumnNameValues.DEBIT.value: [10.0],
                }
            ),
            -10.0,
        ),
        (
            pd.DataFrame(
                {
                    ColumnNameValues.CREDIT.value: [None],
                    ColumnNameValues.DEBIT.value: [None],
                }
            ),
            0.0,
        ),
    ],
)
def test__calculate_result(input_data: pd.DataFrame, expected: float) -> None:
    """Test function calculate_result."""
    result = PandasAlgorithmGeneralLedger.calculate_result(input_data.iloc[0])
    assert result == expected
