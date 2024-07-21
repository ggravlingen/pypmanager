"""Tests for pandas algorithm."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import ColumnNameValues, TransactionTypeValues
from pypmanager.ingest.transaction.pandas_algorithm import PandasAlgorithm
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from tests.conftest import DataFactory


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


@pytest.mark.parametrize(
    ("number", "expected_result"),
    [
        (None, None),
        ("-", 0),
        ("500 000 000.0", 500000000.0),
        ("500,0", 500.0),
    ],
)
def test_cleanup_number(number: str | None, expected_result: float | None) -> None:
    """Test function _cleanup_number."""
    result = PandasAlgorithm.cleanup_number(number)
    assert result == expected_result


def test_cleanup_number__raise_value_error() -> None:
    """Test function _cleanup_number for invalid number."""
    with pytest.raises(ValueError, match="Unable to parse abc"):
        PandasAlgorithm.cleanup_number("abc")


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        # Amount is None, which leads to an early return
        (
            pd.DataFrame(
                {
                    ColumnNameValues.AMOUNT.value: [None],
                    ColumnNameValues.COMMISSION.value: [None],
                }
            ),
            0.0,
        ),
        # Amount is 1.00 but commission is None
        (
            pd.DataFrame(
                {
                    ColumnNameValues.AMOUNT.value: [1.0],
                    ColumnNameValues.COMMISSION.value: [None],
                }
            ),
            1.0,
        ),
        # Both amount and commission are True
        (
            pd.DataFrame(
                {
                    ColumnNameValues.AMOUNT.value: [1.0],
                    ColumnNameValues.COMMISSION.value: [2.0],
                }
            ),
            3.0,
        ),
    ],
)
def test_calculate_cash_flow_nominal(
    row: pd.DataFrame,
    expected: float,
) -> None:
    """Test function calculate_CASH_FLOW_NET_FEE_NOMINAL."""
    result = PandasAlgorithm.calculate_cash_flow_net_fee_nominal(row.iloc[0])
    assert result == expected


def test_calculate_adjusted_price_per_unit(
    data_factory: type[DataFactory],
) -> None:
    """Test function calculate_adjusted_price_per_unit."""
    factory = data_factory()
    df_mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone),
            no_traded=10.0,
            price=10.0,
        )
        .buy(
            transaction_date=datetime(2021, 1, 2, tzinfo=Settings.system_time_zone),
            no_traded=10.0,
            price=20.0,
        )
        .sell(
            transaction_date=datetime(2021, 1, 3, tzinfo=Settings.system_time_zone),
            no_traded=3.0,
        )
        .sell(
            transaction_date=datetime(2021, 1, 4, tzinfo=Settings.system_time_zone),
            no_traded=17.0,
        )
        .buy(
            transaction_date=datetime(2021, 1, 5, tzinfo=Settings.system_time_zone),
            no_traded=100.0,
            price=1.0,
        )
        .buy(
            transaction_date=datetime(2021, 1, 6, tzinfo=Settings.system_time_zone),
            no_traded=100.0,
            price=3.0,
        )
        .df_transaction_list
    )
    df_mocked_transactions = df_mocked_transactions.sort_values(
        [
            ColumnNameValues.NAME.value,
            ColumnNameValues.TRANSACTION_DATE.value,
            ColumnNameValues.TRANSACTION_TYPE.value,
        ],
        ascending=[True, True, True],
    )
    # Calculate turnover
    df_mocked_transactions[ColumnNameValues.AMOUNT.value] = (
        df_mocked_transactions[ColumnNameValues.NO_TRADED.value]
        * df_mocked_transactions[ColumnNameValues.PRICE.value]
    )
    df_mocked_transactions[ColumnNameValues.ADJUSTED_QUANTITY_HELD.value] = (
        df_mocked_transactions.apply(
            lambda x: (
                (
                    x[ColumnNameValues.TRANSACTION_TYPE.value]
                    == TransactionTypeValues.BUY.value
                )
                - (
                    x[ColumnNameValues.TRANSACTION_TYPE.value]
                    == TransactionTypeValues.SELL.value
                )
            )
            * x[ColumnNameValues.NO_TRADED.value],
            axis=1,
        )
    )
    df_mocked_transactions[ColumnNameValues.ADJUSTED_QUANTITY_HELD.value] = (
        df_mocked_transactions.groupby(
            ColumnNameValues.NAME.value
        )[ColumnNameValues.ADJUSTED_QUANTITY_HELD.value].cumsum()
    )

    df_mocked_transactions = df_mocked_transactions.groupby(
        ColumnNameValues.NAME.value
    ).apply(PandasAlgorithm.calculate_adjusted_price_per_unit, include_groups=False)

    assert len(df_mocked_transactions) == 6
    expected_values = [10.0, 15.0, 15.0, np.nan, 1.0, 2.0]
    actual_values = df_mocked_transactions[
        ColumnNameValues.PRICE_PER_UNIT.value
    ].to_numpy()

    assert_array_equal(actual_values, expected_values)
