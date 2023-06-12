"""Test class CalculateAggregates."""

from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from pypmanager.loader_transaction.calculate_aggregates_v2 import CalculateAggregates
from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues
import numpy as np


def test_interest_transaction() -> None:
    """Test interest transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: 100.0,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.BROKER: "Broker",
                ColumnNameValues.CF_EX_COMMISSION: None,
                ColumnNameValues.COMMISSION: None,
                ColumnNameValues.COST_BASIS_DELTA: None,
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.NAME: "Name A",
                ColumnNameValues.NO_HELD: None,
                ColumnNameValues.PRICE: None,
                ColumnNameValues.REALIZED_PNL: 100.0,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: 100.0,
                ColumnNameValues.SOURCE: "Source",
                ColumnNameValues.TRANSACTION_CASH_FLOW: 100.0,
                ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
            }
        ]
    )
    expected_df = expected_df.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = [
        {
            ColumnNameValues.AMOUNT: 100.0,
            ColumnNameValues.BROKER: "Broker",
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.NAME: "Name A",
            ColumnNameValues.SOURCE: "Source",
            ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
        }
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)


def test_dividend_transaction() -> None:
    """Test dividend transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: 100.0,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.BROKER: "Broker",
                ColumnNameValues.CF_EX_COMMISSION: None,
                ColumnNameValues.COMMISSION: None,
                ColumnNameValues.COST_BASIS_DELTA: None,
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.NAME: "Name A",
                ColumnNameValues.NO_HELD: None,
                ColumnNameValues.PRICE: None,
                ColumnNameValues.REALIZED_PNL: 100.0,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: 100.0,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                ColumnNameValues.SOURCE: "Source",
                ColumnNameValues.TRANSACTION_CASH_FLOW: 100.0,
                ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.DIVIDEND,
            }
        ]
    )
    expected_df = expected_df.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = [
        {
            ColumnNameValues.AMOUNT: 100.0,
            ColumnNameValues.BROKER: "Broker",
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.NAME: "Name A",
            ColumnNameValues.SOURCE: "Source",
            ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.DIVIDEND,
        }
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)


def test_buy_transaction() -> None:
    """Test buy transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: -100.0,
                ColumnNameValues.AVG_PRICE: 10.0,
                ColumnNameValues.BROKER: "Broker",
                ColumnNameValues.CF_EX_COMMISSION: -100.0,
                ColumnNameValues.COMMISSION: -5.0,
                ColumnNameValues.COST_BASIS_DELTA: -100.0,
                ColumnNameValues.SUM_COST_BASIS_DELTA: -100.0,
                ColumnNameValues.NAME: "Name A",
                ColumnNameValues.NO_HELD: 10.0,
                ColumnNameValues.PRICE: 10.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                ColumnNameValues.SOURCE: "Source",
                ColumnNameValues.TRANSACTION_CASH_FLOW: -105.0,
                ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
            }
        ]
    )
    expected_df = expected_df.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = [
        {
            ColumnNameValues.AMOUNT: -100.0,
            ColumnNameValues.BROKER: "Broker",
            ColumnNameValues.COMMISSION: -5.0,
            ColumnNameValues.NAME: "Name A",
            ColumnNameValues.NO_TRADED: 10.0,
            ColumnNameValues.PRICE: 10.0,
            ColumnNameValues.SOURCE: "Source",
            ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
        }
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)


def test_sell_transaction() -> None:
    """Test sell transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: -100.0,
                ColumnNameValues.AVG_PRICE: 10.0,
                ColumnNameValues.BROKER: "Broker",
                ColumnNameValues.CF_EX_COMMISSION: -100.0,
                ColumnNameValues.COMMISSION: -5.0,
                ColumnNameValues.COST_BASIS_DELTA: -100.0,
                ColumnNameValues.SUM_COST_BASIS_DELTA: -100.0,
                ColumnNameValues.NAME: "Name A",
                ColumnNameValues.NO_HELD: 10.0,
                ColumnNameValues.PRICE: 10.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                ColumnNameValues.SOURCE: "Source",
                ColumnNameValues.TRANSACTION_CASH_FLOW: -105.0,
                ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
            },
            {
                ColumnNameValues.AMOUNT: 200.0,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.BROKER: "Broker",
                ColumnNameValues.CF_EX_COMMISSION: 200.0,
                ColumnNameValues.COMMISSION: -10.0,
                ColumnNameValues.COST_BASIS_DELTA: None,
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.NAME: "Name A",
                ColumnNameValues.NO_HELD: None,
                ColumnNameValues.PRICE: 20.0,
                ColumnNameValues.REALIZED_PNL: 100.0,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: 100.0,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                ColumnNameValues.SOURCE: "Source",
                ColumnNameValues.TRANSACTION_CASH_FLOW: 190.0,
                ColumnNameValues.TRANSACTION_DATE: datetime(2023, 5, 1),
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
            },
        ]
    )
    expected_df = expected_df.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = [
        {
            ColumnNameValues.AMOUNT: -100.0,
            ColumnNameValues.BROKER: "Broker",
            ColumnNameValues.COMMISSION: -5.0,
            ColumnNameValues.NAME: "Name A",
            ColumnNameValues.NO_TRADED: 10.0,
            ColumnNameValues.PRICE: 10.0,
            ColumnNameValues.SOURCE: "Source",
            ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
        },
        {
            ColumnNameValues.AMOUNT: 200.0,
            ColumnNameValues.BROKER: "Broker",
            ColumnNameValues.COMMISSION: -10.0,
            ColumnNameValues.NAME: "Name A",
            ColumnNameValues.NO_TRADED: -10.0,
            ColumnNameValues.PRICE: 20.0,
            ColumnNameValues.SOURCE: "Source",
            ColumnNameValues.TRANSACTION_DATE: datetime(2023, 5, 1),
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
        },
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = CalculateAggregates(security_transactions=df_test)

    compare_df = data.output_data
    compare_df = compare_df.replace({np.nan: None})

    assert_frame_equal(compare_df, expected_df, check_dtype=False)
