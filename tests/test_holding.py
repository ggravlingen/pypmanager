"""Test Holding."""
import numpy as np
from numpy.testing import assert_allclose
import pandas as pd
import pytest

from pypmanager.analytics.holding import _calculate_aggregates
from pypmanager.loader_transaction.const import TransactionTypeValues

TEST_DATA = [
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": -10 * 100,
        "no_traded": 10,
        "price": 100,
        "commission": 5,
    },
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": -20 * 50,
        "no_traded": 20,
        "price": 50,
        "commission": 10,
    },
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.DIVIDEND,
        "amount": 1 * 20,
        "no_traded": 1,
        "price": 20,
        "commission": 0,
    },
    {
        "name": "CASH",
        "transaction_type": TransactionTypeValues.INTEREST,
        "amount": 1 * 20,
        "no_traded": 1,
        "price": 20,
        "commission": 0,
    },
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.SELL,
        "amount": 30 * 100,
        "no_traded": -30,
        "price": 100,
        "commission": 100,
    },
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.FEE,
        "amount": -20,
        "no_traded": np.nan,
        "price": np.nan,
        "commission": np.nan,
    },
]


def test_calculate_aggregates() -> None:
    """Test _calculate_aggregates."""
    data = pd.DataFrame(TEST_DATA)
    result = _calculate_aggregates(data)

    assert result.name.to_list() == ["AAPL", "AAPL", "AAPL", "CASH", "AAPL", "AAPL"]
    assert result.transaction_type.to_list() == [
        "buy",
        "buy",
        "dividend",
        "interest",
        "sell",
        "fee",
    ]
    assert result.amount.to_list() == [-1000, -1000, 20, 20, 3000, -20]

    assert_allclose(
        result.no_traded.to_list(),
        [10, 20, 1, 1, -30, np.nan],
        rtol=1e-9,
        atol=0,
        equal_nan=True,
    )

    assert_allclose(
        result.price.to_list(),
        [100, 50, 20, 20, 100, np.nan],
        rtol=1e-9,
        atol=0,
        equal_nan=True,
    )

    assert_allclose(
        result.commission.to_list(),
        [5, 10, 0, 0, 100, np.nan],
        rtol=1e-9,
        atol=0,
        equal_nan=True,
    )

    assert result.cumulative_buy_amount.to_list() == [1000, 2000, 2000, 2000, 0, 0]

    assert pd.isna(result.realized_pnl.to_list()[0])
    assert pd.isna(result.realized_pnl.to_list()[1])
    assert pytest.approx(result.realized_pnl.sum()) == 905

    assert result.cumulative_invested_amount.to_list()[:2] == [1005, 2015]

    assert pytest.approx(result.average_price.to_list()[0]) == 100.5
    assert pytest.approx(result.average_price.to_list()[1]) == 67.166667
    assert result.average_price.to_list()[4] is None

    assert result.cumulative_dividends.to_list() == [0, 0, 20, 20, 20, 20]
