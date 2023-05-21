"""Test Holding."""
from datetime import datetime

import numpy as np
from numpy.testing import assert_allclose
import pandas as pd
import pytest

from pypmanager.loader_transaction.calculate_aggregates import (
    calculate_aggregates,
    to_valid_column_name,
)
from pypmanager.loader_transaction.const import TransactionTypeValues

TEST_DATA = [
    {
        "report_date": datetime(2023, 5, 8, 12, 0, 0),
        "broker": "Acoount 1",
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": -10 * 100,
        "no_traded": 10,
        "price": 100,
        "commission": 5,
        "fx_rate": 1,
    },
    {
        "report_date": datetime(2023, 5, 8, 12, 1, 0),
        "broker": "Acoount 1",
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": -20 * 50,
        "no_traded": 20,
        "price": 50,
        "commission": 10,
        "fx_rate": 1,
    },
    {
        "report_date": datetime(2023, 5, 8, 12, 2, 0),
        "broker": "Acoount 1",
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.DIVIDEND,
        "amount": 1 * 20,
        "no_traded": 1,
        "price": 20,
        "commission": 0,
        "fx_rate": 1,
    },
    {
        "report_date": datetime(2023, 5, 8, 12, 3, 0),
        "broker": "Acoount 1",
        "name": "CASH",
        "transaction_type": TransactionTypeValues.INTEREST,
        "amount": 1 * 20,
        "no_traded": 1,
        "price": 20,
        "commission": 0,
        "fx_rate": 1,
    },
    {
        "report_date": datetime(2023, 5, 8, 12, 4, 0),
        "broker": "Acoount 1",
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.SELL,
        "amount": 30 * 100,
        "no_traded": -30,
        "price": 100,
        "commission": 100,
        "fx_rate": 1,
    },
    {
        "report_date": datetime(2023, 5, 8, 12, 5, 0),
        "broker": "Acoount 1",
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.FEE,
        "amount": -20,
        "no_traded": np.nan,
        "price": np.nan,
        "commission": np.nan,
        "fx_rate": 1,
    },
    {
        "report_date": datetime(2023, 5, 8, 12, 6, 0),
        "broker": "Acoount 2",
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": -20 * 50,
        "no_traded": 20,
        "price": 50,
        "commission": 10,
        "fx_rate": 1,
    },
]


def test_calculate_aggregates__buy_sell__same_ccy() -> None:
    """Test _calculate_aggregates for buy/sell in the same currency."""
    sample_data = [
        {
            "report_date": datetime(2023, 5, 8, 12, 0, 0),
            "broker": "Acoount 1",
            "name": "AAPL",
            "transaction_type": TransactionTypeValues.BUY,
            "amount": -10 * 100,
            "no_traded": 10,
            "price": 100,
            "commission": -5,
            "fx_rate": 1,
        },
        {
            "report_date": datetime(2023, 5, 8, 13, 0, 0),
            "broker": "Acoount 1",
            "name": "AAPL",
            "transaction_type": TransactionTypeValues.BUY,
            "amount": -20 * 50,
            "no_traded": 20,
            "price": 50,
            "commission": -10,
            "fx_rate": 1,
        },
        {
            "report_date": datetime(2023, 5, 8, 14, 0, 0),
            "broker": "Acoount 1",
            "name": "AAPL",
            "transaction_type": TransactionTypeValues.SELL,
            "amount": 30 * 100,
            "no_traded": 30,
            "price": 100,
            "commission": -100,
            "fx_rate": 1,
        },
    ]
    data = pd.DataFrame(sample_data)
    data.set_index("report_date")
    result = calculate_aggregates(data)

    assert result.name.to_list() == ["AAPL", "AAPL", "AAPL"]
    assert result.amount.to_list() == [-1000, -1000, 3000]
    assert result.commission.to_list() == [-5, -10, -100]
    assert result.fx_rate.to_list() == [1.0, 1.0, 1.0]
    assert result.average_fx_rate.to_list() == [1.0, 1.0, 0.0]
    assert_allclose(
        result.average_price.to_list(),
        [100.500000, 67.166667, np.nan],
        rtol=1e-2,
        atol=0,
        equal_nan=True,
    )
    assert result.cash_flow_base_ccy.to_list() == [-1005, -1010, 2900]
    assert result.cumulative_invested_amount.to_list() == [-1005, -2015, 885.0]
    assert result.cumulative_buy_amount.to_list() == [1000, 2000, 2000]
    assert result.cumulative_buy_volume.to_list() == [10, 30, 0]
    assert_allclose(
        result.realized_pnl_equity.to_list(),
        [0.0, 0.0, 885.0],
        rtol=1e-2,
        atol=0,
        equal_nan=True,
    )
    assert_allclose(
        result.realized_pnl_fx.to_list(),
        [0.0, 0.0, 0.0],
        rtol=1e-2,
        atol=0,
        equal_nan=True,
    )

    assert_allclose(
        result.realized_pnl.to_list(),
        [np.nan, np.nan, 885.0],
        rtol=1e-2,
        atol=0,
        equal_nan=True,
    )


def test_calculate_aggregates() -> None:
    """Test _calculate_aggregates."""
    data = pd.DataFrame(TEST_DATA)
    data.set_index("report_date")
    result = calculate_aggregates(data)

    assert result.name.to_list() == [
        "AAPL",
        "AAPL",
        "AAPL",
        "CASH",
        "AAPL",
        "AAPL",
        "AAPL",
    ]
    assert result.transaction_type.to_list() == [
        "buy",
        "buy",
        "dividend",
        "interest",
        "sell",
        "fee",
        "buy",
    ]
    assert result.amount.to_list() == [-1000, -1000, 20, 20, 3000, -20, -1000]

    assert_allclose(
        result.no_traded.to_list(),
        [10, 20, 1, 1, -30, np.nan, 20],
        rtol=1e-9,
        atol=0,
        equal_nan=True,
    )

    assert_allclose(
        result.price.to_list(),
        [100, 50, 20, 20, 100, np.nan, 50],
        rtol=1e-9,
        atol=0,
        equal_nan=True,
    )

    assert_allclose(
        result.commission.to_list(),
        [5, 10, 0, 0, 100, np.nan, 10],
        rtol=1e-9,
        atol=0,
        equal_nan=True,
    )

    assert pd.isna(result.realized_pnl.to_list()[0])
    assert pd.isna(result.realized_pnl.to_list()[1])
    assert pytest.approx(result.realized_pnl.sum()) == 935

    assert_allclose(
        result.average_price.to_list(),
        [99.5, 66.166667, 66.166667, 66.166667, np.nan, np.nan, 49.5],
        rtol=1e-2,
        atol=0,
        equal_nan=True,
    )

    # Cumulative amounts
    assert result.cumulative_buy_amount.to_list() == [
        1000,
        2000,
        2000,
        2000,
        2000,
        0,
        1000,
    ]
    assert result.cumulative_invested_amount.to_list()[:2] == [-995.0, -1985.0]
    assert result.cumulative_dividends.to_list() == [0, 0, 20, 20, 20, 20, 20]


@pytest.mark.parametrize(
    "input_string, expected_output",
    [
        ("Column Name", "column_name"),
        ("(some) Characters - Here", "some_characters__here"),
        ("123.45 %", "_12345_"),
        ("$special!@chars", "specialchars"),
        (" Spaces at beginning and end ", "_spaces_at_beginning_and_end_"),
    ],
)
def test_to_valid_column_name(input_string, expected_output):
    """Test function to_valid_column_name."""
    result = to_valid_column_name(input_string)

    # assert that the result matches the expected output
    assert result == expected_output
