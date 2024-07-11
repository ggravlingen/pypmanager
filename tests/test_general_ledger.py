"""Tests for the general ledger."""

import pandas as pd

from pypmanager.general_ledger import GeneralLedger
from pypmanager.general_ledger.transation_macro import _amend_row
from pypmanager.ingest.transaction import (
    AccountNameValues,
    ColumnNameValues,
    TransactionTypeValues,
)


def test_amend_row__buy() -> None:
    """Test output data for a buy transaction."""
    input_row = {
        ColumnNameValues.AMOUNT: 100,
        ColumnNameValues.CASH_FLOW_LOCAL: 100,
        ColumnNameValues.AVG_PRICE: 100,
        ColumnNameValues.NO_TRADED: 100,
        ColumnNameValues.REALIZED_PNL: None,
        ColumnNameValues.REALIZED_PNL_EQ: None,
        ColumnNameValues.REALIZED_PNL_FX: None,
        ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
    }
    expected_result = [
        # Credit row
        {
            ColumnNameValues.AMOUNT: 100,
            ColumnNameValues.AVG_PRICE: 100,
            ColumnNameValues.CASH_FLOW_LOCAL: 100,
            ColumnNameValues.CREDIT: -100,
            ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
            ColumnNameValues.NO_TRADED: 100,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.BUY,
        },
        # Debit row
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: 100,
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.DEBIT: -100,
            ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.BUY,
        },
    ]

    result = _amend_row(input_row)

    assert result == expected_result


def test_amend_row__fee() -> None:
    """Test output data for a fee transaction."""
    input_row = {
        ColumnNameValues.AMOUNT: -100,
        ColumnNameValues.CASH_FLOW_LOCAL: -100,
        ColumnNameValues.AVG_PRICE: None,
        ColumnNameValues.NO_TRADED: None,
        ColumnNameValues.REALIZED_PNL: -100,
        ColumnNameValues.REALIZED_PNL_EQ: None,
        ColumnNameValues.REALIZED_PNL_FX: None,
        ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.FEE,
    }
    expected_result = [
        {
            ColumnNameValues.AMOUNT: -100,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: -100,
            ColumnNameValues.CREDIT: 100,
            ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.REALIZED_PNL: -100,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.FEE,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: -100,
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.DEBIT: 100,
            ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: -100,
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.DEBIT: 100,
            ColumnNameValues.ACCOUNT: AccountNameValues.IS_FEE,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
        },
    ]
    result = _amend_row(input_row)

    assert result == expected_result


def test_amend_row__sell() -> None:
    """Test output data for a sell transaction."""
    input_row = {
        ColumnNameValues.AMOUNT: 10000,
        ColumnNameValues.CASH_FLOW_LOCAL: 10000,
        ColumnNameValues.AVG_PRICE: 100.0,
        ColumnNameValues.NO_TRADED: 100,
        ColumnNameValues.REALIZED_PNL: 50,
        ColumnNameValues.REALIZED_PNL_EQ: 50,
        ColumnNameValues.REALIZED_PNL_FX: 0,
        ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
    }
    expected_result = [
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: 100.0,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            ColumnNameValues.CREDIT: 10000,
            ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: 0,
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.CREDIT: 50,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.ACCOUNT: AccountNameValues.IS_PNL,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.CREDIT: 50,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
            ColumnNameValues.NO_TRADED: None,
            ColumnNameValues.PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
        {
            ColumnNameValues.AMOUNT: 10000,
            ColumnNameValues.AVG_PRICE: 100.0,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            ColumnNameValues.COMMISSION: None,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.DEBIT: 10000,
            ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
            ColumnNameValues.NO_TRADED: 100,
            ColumnNameValues.REALIZED_PNL: 50,
            ColumnNameValues.REALIZED_PNL_EQ: 50,
            ColumnNameValues.REALIZED_PNL_FX: None,
            ColumnNameValues.TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
    ]
    result = _amend_row(input_row)

    assert result == expected_result


def test_class_general_ledger(df_transaction_data_factory: pd.DataFrame) -> None:
    """Test functionality of GeneralLedger."""
    fixture_df_transaction_data = df_transaction_data_factory(no_rows=1)

    ledger = GeneralLedger(transactions=fixture_df_transaction_data)

    assert len(ledger.transactions) == 1
