"""Test class CalculateAggregates."""

from datetime import date

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from pypmanager.general_ledger.calculate_aggregates import CalculateAggregates
from pypmanager.ingest.transaction import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)


def test_interest_transaction() -> None:
    """Test interest transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: 100.0,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: 100.0,
                ColumnNameValues.CF_EX_COMMISSION: None,
                TransactionRegistryColNameValues.SOURCE_FEE: None,
                ColumnNameValues.COST_BASIS_DELTA: None,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: None,
                TransactionRegistryColNameValues.SOURCE_VOLUME: None,
                TransactionRegistryColNameValues.SOURCE_PRICE: None,
                ColumnNameValues.REALIZED_PNL: 100.0,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: 100.0,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.TRANSACTION_CASH_FLOW: 100.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 1
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.INTEREST
                ),
            },
        ],
    )
    expected_df = expected_df.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = [
        {
            ColumnNameValues.AMOUNT: 100.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 1),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.INTEREST
            ),
        },
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)


def test_dividend_transaction() -> None:
    """Test dividend transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: 100.0,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: 100.0,
                ColumnNameValues.CF_EX_COMMISSION: None,
                TransactionRegistryColNameValues.SOURCE_FEE: None,
                ColumnNameValues.COST_BASIS_DELTA: None,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: None,
                TransactionRegistryColNameValues.SOURCE_VOLUME: None,
                TransactionRegistryColNameValues.SOURCE_PRICE: None,
                ColumnNameValues.REALIZED_PNL: 100.0,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: 100.0,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.TRANSACTION_CASH_FLOW: 100.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 1
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.DIVIDEND
                ),
            },
        ],
    )
    expected_df = expected_df.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = [
        {
            ColumnNameValues.AMOUNT: 100.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 1),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.DIVIDEND
            ),
        },
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)


def test_buy_transaction() -> None:
    """Test buy transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: -100.0,
                ColumnNameValues.AVG_PRICE: 10.0,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: -105.0,
                ColumnNameValues.CF_EX_COMMISSION: -100.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -5.0,
                ColumnNameValues.COST_BASIS_DELTA: -100.0,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: 10.0,
                TransactionRegistryColNameValues.SOURCE_VOLUME: 10.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 10.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: -100.0,
                ColumnNameValues.TRANSACTION_CASH_FLOW: -105.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 1
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.BUY
                ),
            },
        ],
    )
    expected_df = expected_df.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = [
        {
            ColumnNameValues.AMOUNT: -100.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -5.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: 10.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 10.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 1),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.BUY
            ),
        },
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)


def test_sell_transaction() -> None:
    """Test sell transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: -100.0,
                ColumnNameValues.AVG_PRICE: 10.0,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: -105.0,
                ColumnNameValues.CF_EX_COMMISSION: -100.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -5.0,
                ColumnNameValues.COST_BASIS_DELTA: -100.0,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: 10.0,
                TransactionRegistryColNameValues.SOURCE_VOLUME: 10.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 10.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: -100.0,
                ColumnNameValues.TRANSACTION_CASH_FLOW: -105.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 1
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.BUY
                ),
            },
            {
                ColumnNameValues.AMOUNT: 200.0,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CF_EX_COMMISSION: 200.0,
                ColumnNameValues.CASH_FLOW_LOCAL: 190.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -10.0,
                ColumnNameValues.COST_BASIS_DELTA: None,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: None,
                TransactionRegistryColNameValues.SOURCE_VOLUME: -10.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 20.0,
                ColumnNameValues.REALIZED_PNL: 100.0,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: 100.0,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.TRANSACTION_CASH_FLOW: 190.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 5, 1
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.SELL
                ),
            },
        ],
    )
    expected_df = expected_df.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = [
        {
            ColumnNameValues.AMOUNT: -100.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -5.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: 10.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 10.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 1),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.BUY
            ),
        },
        {
            ColumnNameValues.AMOUNT: 200.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -10.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: -10.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 20.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 5, 1),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.SELL
            ),
        },
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = CalculateAggregates(security_transactions=df_test)

    compare_df = data.output_data
    compare_df = compare_df.replace({np.nan: None})
    expected_df = expected_df.replace({np.nan: None})

    assert_frame_equal(compare_df, expected_df, check_dtype=False)


def test_buy_sell_sequence() -> None:
    """Test a sequence of buy and sells."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.AMOUNT: -1500.0,
                ColumnNameValues.AVG_PRICE: 10.0,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: -1599.0,
                ColumnNameValues.CF_EX_COMMISSION: -1500.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
                ColumnNameValues.COST_BASIS_DELTA: -1500.0,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: 150.0,
                TransactionRegistryColNameValues.SOURCE_VOLUME: 150.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 10.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: -1500.0,
                ColumnNameValues.TRANSACTION_CASH_FLOW: -1599.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 1
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.BUY
                ),
            },
            {
                ColumnNameValues.AMOUNT: -1224.0,
                ColumnNameValues.AVG_PRICE: 11.6667,
                ColumnNameValues.AVG_FX: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: -1224.0,
                ColumnNameValues.CF_EX_COMMISSION: -1125.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
                ColumnNameValues.COST_BASIS_DELTA: -1125.0,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: 225.0,
                TransactionRegistryColNameValues.SOURCE_VOLUME: 75.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 15.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_COMMISSION: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: None,
                ColumnNameValues.REALIZED_PNL_INTEREST: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: -2625.0,
                ColumnNameValues.TRANSACTION_CASH_FLOW: -1224.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 2
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.BUY
                ),
            },
            {
                ColumnNameValues.AMOUNT: 1000.0,
                ColumnNameValues.AVG_PRICE: 11.6667,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: 901.0,
                ColumnNameValues.CF_EX_COMMISSION: 1000.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
                ColumnNameValues.COST_BASIS_DELTA: 583.33,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: 175.0,
                TransactionRegistryColNameValues.SOURCE_VOLUME: -50.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 20.0,
                ColumnNameValues.REALIZED_PNL: 416.67,
                ColumnNameValues.REALIZED_PNL_EQ: 416.67,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: -2041.67,
                ColumnNameValues.TRANSACTION_CASH_FLOW: 901.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.SELL
                ),
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 3
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            },
            {
                ColumnNameValues.AMOUNT: -625.0,
                ColumnNameValues.AVG_PRICE: 13.3333,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: -724.0,
                ColumnNameValues.CF_EX_COMMISSION: -625.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
                ColumnNameValues.COST_BASIS_DELTA: -625,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: 200.0,
                TransactionRegistryColNameValues.SOURCE_VOLUME: 25.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 25.0,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.REALIZED_PNL_EQ: None,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: -2666.67,
                ColumnNameValues.TRANSACTION_CASH_FLOW: -724.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.BUY
                ),
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 4
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            },
            {
                ColumnNameValues.AMOUNT: 5000.0,
                ColumnNameValues.AVG_PRICE: None,
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
                ColumnNameValues.CASH_FLOW_LOCAL: 4901.0,
                ColumnNameValues.CF_EX_COMMISSION: 5000.0,
                TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
                ColumnNameValues.COST_BASIS_DELTA: None,
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
                ColumnNameValues.NO_HELD: None,
                TransactionRegistryColNameValues.SOURCE_VOLUME: -200.0,
                TransactionRegistryColNameValues.SOURCE_PRICE: 25.0,
                ColumnNameValues.REALIZED_PNL: 2333.33,
                ColumnNameValues.REALIZED_PNL_EQ: 2333.33,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
                ColumnNameValues.SUM_COST_BASIS_DELTA: None,
                ColumnNameValues.TRANSACTION_CASH_FLOW: 4901.0,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                    TransactionTypeValues.SELL
                ),
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(
                    2023, 4, 5
                ),
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            },
        ],
    )
    expected_df = expected_df.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = [
        {
            ColumnNameValues.AMOUNT: -1500.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: 150.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 10.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 1),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.BUY
            ),
        },
        {
            ColumnNameValues.AMOUNT: -1224.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: 75.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 15.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 2),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.BUY
            ),
        },
        {
            ColumnNameValues.AMOUNT: 1000.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: -50.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 20.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 3),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.SELL
            ),
        },
        {
            ColumnNameValues.AMOUNT: -625.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: 25.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 25.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 4),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.BUY
            ),
        },
        {
            ColumnNameValues.AMOUNT: 5000.0,
            TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker",
            TransactionRegistryColNameValues.SOURCE_FEE: -99.0,
            TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
            TransactionRegistryColNameValues.SOURCE_ISIN: "isin",
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Name A",
            TransactionRegistryColNameValues.SOURCE_VOLUME: -200.0,
            TransactionRegistryColNameValues.SOURCE_PRICE: 25.0,
            TransactionRegistryColNameValues.SOURCE_FILE.value: "Source",
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE: date(2023, 4, 5),
            TransactionRegistryColNameValues.META_TRANSACTION_YEAR: 2023,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.SELL
            ),
        },
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
    )

    data = CalculateAggregates(security_transactions=df_test)

    compare_df = data.output_data
    compare_df = compare_df.replace({np.nan: None})
    expected_df = expected_df.replace({np.nan: None})

    assert_frame_equal(compare_df, expected_df, check_dtype=False)
