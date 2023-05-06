"""Tests."""
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from pypmanager.loader_market_data.avanza import AvanzaLoader
from pypmanager.loader_transaction.base_loader import (
    _cleanup_number,
    _normalize_amount,
    _normalize_no_traded,
    _replace_name,
)
from pypmanager.loader_transaction.const import TransactionTypeValues
from pypmanager.loader_transaction.lysa import LysaLoader
from pypmanager.loader_transaction.misc import MiscLoader
from pypmanager.settings import Settings


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            pd.Series(
                {"name": "Foo", "transaction_type": TransactionTypeValues.INTEREST},
            ),
            "Cash and equivalents",
        ),
        (
            pd.Series(
                {"name": "Foo", "transaction_type": TransactionTypeValues.BUY},
            ),
            "Foo",
        ),
    ],
)
def test_replace_name(data, expected) -> None:
    """Test function _replace_name."""
    result = _replace_name(data)
    assert result == expected


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


@pytest.mark.parametrize(
    "number, expected_result",
    [
        ("-", 0),  # ok
        ("500 000 000.0", 500000000.0),  # ok
        ("500,0", 500.0),
    ],
)
def test_cleanup_number(number, expected_result) -> None:
    """Test function _cleanup_number."""
    result = _cleanup_number(number)

    assert result == expected_result


@patch.object(Settings, "DIR_DATA", "tests/fixtures/")
def test_avanza_loder() -> None:
    """Test AvanzaLoader."""
    df = AvanzaLoader().df

    assert len(df) > 0


@patch.object(Settings, "DIR_DATA", "tests/fixtures/")
def test_lysa_loader() -> None:
    """Test LysaLoader."""
    df = LysaLoader().df

    assert len(df) > 0


@patch.object(Settings, "DIR_DATA", "tests/fixtures/")
def test_misc_loader() -> None:
    """Test MiscLoader."""
    df = MiscLoader().df

    assert len(df) > 0
