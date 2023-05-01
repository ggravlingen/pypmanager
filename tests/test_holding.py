"""Test Holding."""
import pandas as pd
import pytest

from pypmanager.data_loader import TransactionTypeValues
from pypmanager.holding import _calculate_aggregates

TEST_DATA = [
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": 10 * 100,
        "no_traded": 10,
        "price": 100,
        "commission": 5,
    },
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.BUY,
        "amount": 20 * 50,
        "no_traded": 20,
        "price": 50,
        "commission": 10,
    },
    {
        "name": "AAPL",
        "transaction_type": TransactionTypeValues.SELL,
        "amount": 30 * 100,
        "no_traded": 30,
        "price": 100,
        "commission": 100,
    },
]


def test_calculate_aggregates() -> None:
    """Test _calculate_aggregates."""
    data = pd.DataFrame(TEST_DATA)
    result = _calculate_aggregates(data, "AAPL")

    assert result.name.to_list() == ["AAPL"] * 3
    assert result.transaction_type.to_list() == ["buy", "buy", "sell"]
    assert result.amount.to_list() == [1000, 1000, 3000]
    assert result.no_traded.to_list() == [10, 20, 30]
    assert result.price.to_list() == [100, 50, 100]
    assert result.commission.to_list() == [5, 10, 100]

    assert result.cumulative_buy_amount.to_list()[:2] == [1000, 2000]
    assert pd.isna(result.cumulative_buy_amount.to_list()[2:3])

    assert pd.isna(result.realized_pnl.to_list()[0])
    assert pd.isna(result.realized_pnl.to_list()[1])
    assert pytest.approx(result.realized_pnl.to_list()[2]) == 885

    assert result.cumulative_invested_amount.to_list()[:2] == [1005, 2015]
    assert pd.isna(result.cumulative_invested_amount.to_list()[2])

    assert pytest.approx(result.average_price.to_list()[0]) == 100.5
    assert pytest.approx(result.average_price.to_list()[1]) == 67.166667
    assert pd.isna(result.average_price.to_list()[2])
