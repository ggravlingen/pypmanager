"""Tests."""
import numpy as np
import pandas as pd
import pytest

from pypmanager.data_loader import (
    TransactionTypeValues,
    _normalize_amount,
    _normalize_no_traded,
)


@pytest.mark.parametrize(
    "row, expected",
    [
        # Test a buy transaction with a specified amount
        (
            pd.Series(
                {"amount": -100, "transaction_type": TransactionTypeValues.BUY},
            ),
            -100,
        ),
        # Test a buy transaction without a specified amount
        (
            pd.Series(
                {
                    "amount": np.nan,
                    "no_traded": 10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.BUY,
                }
            ),
            -100,
        ),
        # Test a sell transaction with a specified amount
        (
            pd.Series({"amount": 100, "transaction_type": TransactionTypeValues.SELL}),
            100,
        ),
        # Test a sell transaction without a specified amount
        (
            pd.Series(
                {
                    "amount": np.nan,
                    "no_traded": 10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.SELL,
                }
            ),
            100,
        ),
        # Test a sell transaction with a negative specified amount
        (
            pd.Series({"amount": -100, "transaction_type": TransactionTypeValues.SELL}),
            100,
        ),
        # Test a buy transaction without a specified amount and a negative number of
        # traded units
        (
            pd.Series(
                {
                    "amount": np.nan,
                    "no_traded": -10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.BUY,
                }
            ),
            -100,
        ),
    ],
)
def test_normalize_amount(row, expected):
    """Test function _normalize_amount."""
    assert _normalize_amount(row) == expected


@pytest.fixture
def data_normalize_no_traded() -> pd.DataFrame:
    """Return test data for normalize_no_traded function."""
    return pd.DataFrame({"transaction_type": ["BUY", "SELL"], "no_traded": [10, -5]})


@pytest.mark.parametrize(
    "trans_type, no_traded, expected",
    [
        (TransactionTypeValues.BUY, 10, 10),
        (TransactionTypeValues.SELL, -5, -5),
    ],
)
def test__normalize_no_traded(trans_type, no_traded, expected):
    """Test function _normalize_no_traded."""
    test_data = pd.DataFrame(
        {"transaction_type": [trans_type], "no_traded": [no_traded]}
    )
    result = _normalize_no_traded(test_data.iloc[0])

    assert result == expected
