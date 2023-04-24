"""Tests."""
from pypmanager.data_loader import TransactionTypeValues, _normalize_amount
import numpy as np
import pandas as pd
import pytest


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
