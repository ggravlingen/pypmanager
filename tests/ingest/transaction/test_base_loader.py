"""Tests."""

from __future__ import annotations

import pandas as pd
import pytest

from pypmanager.ingest.transaction import TransactionTypeValues
from pypmanager.ingest.transaction.base_loader import (
    TransactionLoader,
)
from pypmanager.ingest.transaction.transaction_registry import (
    _cleanup_number,
    _normalize_amount,
    _normalize_no_traded,
)


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        # Test a buy transaction without a specified amount
        (
            pd.Series(
                {
                    "no_traded": 10,
                    "price": 10,
                    "transaction_type": TransactionTypeValues.BUY,
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
                    "transaction_type": TransactionTypeValues.SELL,
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
                    "transaction_type": TransactionTypeValues.BUY,
                },
            ),
            -100,
        ),
    ],
)
def test_normalize_amount(row: pd.Series, expected: int) -> None:
    """Test function _normalize_amount."""
    assert _normalize_amount(row) == expected


@pytest.fixture
def data_normalize_no_traded() -> pd.DataFrame:
    """Return test data for normalize_no_traded function."""
    return pd.DataFrame({"transaction_type": ["BUY", "SELL"], "no_traded": [10, -5]})


@pytest.mark.parametrize(
    ("trans_type", "no_traded", "expected"),
    [
        (TransactionTypeValues.BUY, 10, 10),
        (TransactionTypeValues.SELL, -5, -5),
    ],
)
def test__normalize_no_traded(trans_type: str, no_traded: int, expected: int) -> None:
    """Test function _normalize_no_traded."""
    test_data = pd.DataFrame(
        {"transaction_type": [trans_type], "no_traded": [no_traded]},
    )
    result = _normalize_no_traded(test_data.iloc[0])

    assert result == expected


@pytest.mark.parametrize(
    ("number", "expected_result"),
    [
        ("-", 0),  # ok
        ("500 000 000.0", 500000000.0),  # ok
        ("500,0", 500.0),
    ],
)
def test_cleanup_number(number: str, expected_result: int) -> None:
    """Test function _cleanup_number."""
    result = _cleanup_number(number)

    assert result == expected_result


def test_cleanup_number_raise() -> None:
    """Test function _cleanup_number for invalid number."""
    with pytest.raises(ValueError, match="Unable to parse abc"):
        _cleanup_number("abc")


def test_empty_loader() -> None:
    """Test the base loader class with empty data."""

    class MockLoader(TransactionLoader):
        """Mock the TransactionLoader."""

        file_pattern = "abc123"
        date_format_pattern = "%Y-%m-%d"

        def pre_process_df(self: MockLoader) -> None:
            """Mock method."""

    mock_loader = MockLoader()

    assert len(mock_loader.df_final) == 0
