"""Tests for pandas algorithm."""

from __future__ import annotations

import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import ColumnNameValues, TransactionTypeValues
from pypmanager.ingest.transaction.pandas_algorithm import PandasAlgorithm


@pytest.mark.parametrize(
    ("trans_type", "no_traded", "expected"),
    [
        (TransactionTypeValues.BUY.value, 10, 10),
        (TransactionTypeValues.DIVIDEND.value, 15, 15),
        (TransactionTypeValues.SELL.value, -5, -5),
    ],
)
def test__normalize_no_traded(trans_type: str, no_traded: int, expected: int) -> None:
    """Test function _normalize_no_traded."""
    test_data = pd.DataFrame(
        {"transaction_type": [trans_type], "no_traded": [no_traded]},
    )
    result = PandasAlgorithm.normalize_no_traded(test_data.iloc[0])

    assert result == expected


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        # Case when FX column is missing
        (pd.DataFrame({ColumnNameValues.AMOUNT.value: [1.00]}), 1.00),
        # Case when FX value is NaN
        (pd.DataFrame({ColumnNameValues.FX.value: [pd.NA]}), 1.00),
        # Case when FX value is present and valid
        (pd.DataFrame({ColumnNameValues.FX.value: [1.23]}), 1.23),
    ],
)
def test__normalize_fx(input_data: pd.DataFrame, expected: float) -> None:
    """Test function _normalize_fx."""
    result = PandasAlgorithm.normalize_fx(input_data.iloc[0])
    assert result == expected


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        # Test a buy transaction without a specified amount
        (
            pd.Series(
                {
                    "no_traded": 10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.BUY.value,
                },
            ),
            -100,
        ),
        # Test a sell transaction without a specified amount
        (
            pd.Series(
                {
                    "no_traded": 10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.SELL.value,
                },
            ),
            100,
        ),
        # Test a buy transaction without a specified amount and a negative number of
        # traded units
        (
            pd.Series(
                {
                    "no_traded": -10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.BUY.value,
                },
            ),
            -100,
        ),
        # Test a cashback transaction
        (
            pd.Series(
                {
                    "amount": 100,
                    "transaction_type": TransactionTypeValues.CASHBACK.value,
                },
            ),
            100,
        ),
    ],
)
def test_normalize_amount(row: pd.Series, expected: int) -> None:
    """Test function _normalize_amount."""
    assert PandasAlgorithm.normalize_amount(row) == expected
