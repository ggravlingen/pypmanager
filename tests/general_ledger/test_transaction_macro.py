"""Tests for the transaction macro module."""

from pypmanager.general_ledger.transaction_macro import _amend_row
from pypmanager.ingest.transaction import (
    AccountNameValues,
    ColumnNameValues,
    TransactionTypeValues,
)
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues


def test_amend_row__buy() -> None:
    """Test output data for a buy transaction."""
    input_row = {
        ColumnNameValues.AMOUNT: 100,
        ColumnNameValues.CASH_FLOW_LOCAL: 100,
        ColumnNameValues.AVG_PRICE: 100,
        TransactionRegistryColNameValues.SOURCE_VOLUME: 100,
        ColumnNameValues.REALIZED_PNL: None,
        ColumnNameValues.REALIZED_PNL_EQ: None,
        ColumnNameValues.REALIZED_PNL_FX: None,
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
            TransactionTypeValues.BUY
        ),
    }
    expected_result = [
        # Credit row
        {
            ColumnNameValues.AMOUNT: 100,
            ColumnNameValues.AVG_PRICE: 100,
            ColumnNameValues.CASH_FLOW_LOCAL: 100,
            ColumnNameValues.CREDIT: -100,
            ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
            TransactionRegistryColNameValues.SOURCE_VOLUME: 100,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.BUY
            ),
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.BUY,
        },
        # Debit row
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: 100,
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.DEBIT: -100,
            ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            TransactionRegistryColNameValues.SOURCE_PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: None,
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
        TransactionRegistryColNameValues.SOURCE_VOLUME: None,
        ColumnNameValues.REALIZED_PNL: -100,
        ColumnNameValues.REALIZED_PNL_EQ: None,
        ColumnNameValues.REALIZED_PNL_FX: None,
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
            TransactionTypeValues.FEE
        ),
    }
    expected_result = [
        {
            ColumnNameValues.AMOUNT: -100,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: -100,
            ColumnNameValues.CREDIT: 100,
            ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            ColumnNameValues.REALIZED_PNL: -100,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.FEE
            ),
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: -100,
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            ColumnNameValues.DEBIT: 100,
            ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: -100,
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            ColumnNameValues.DEBIT: 100,
            ColumnNameValues.ACCOUNT: AccountNameValues.IS_FEE,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            TransactionRegistryColNameValues.SOURCE_PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: None,
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
        TransactionRegistryColNameValues.SOURCE_VOLUME: 100,
        ColumnNameValues.REALIZED_PNL: 50,
        ColumnNameValues.REALIZED_PNL_EQ: 50,
        ColumnNameValues.REALIZED_PNL_FX: 0,
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
            TransactionTypeValues.SELL
        ),
    }
    expected_result = [
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: 100.0,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            ColumnNameValues.CREDIT: 10000,
            ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            TransactionRegistryColNameValues.SOURCE_PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: 0,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                TransactionTypeValues.SELL
            ),
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            ColumnNameValues.CREDIT: 50,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.ACCOUNT: AccountNameValues.IS_PNL,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            TransactionRegistryColNameValues.SOURCE_PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
        {
            ColumnNameValues.AMOUNT: None,
            ColumnNameValues.AVG_PRICE: None,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            ColumnNameValues.CREDIT: 50,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
            TransactionRegistryColNameValues.SOURCE_VOLUME: None,
            TransactionRegistryColNameValues.SOURCE_PRICE: None,
            ColumnNameValues.REALIZED_PNL: None,
            ColumnNameValues.REALIZED_PNL_EQ: None,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
        {
            ColumnNameValues.AMOUNT: 10000,
            ColumnNameValues.AVG_PRICE: 100.0,
            ColumnNameValues.CASH_FLOW_LOCAL: 10000,
            TransactionRegistryColNameValues.SOURCE_FEE: None,
            ColumnNameValues.NO_HELD: None,
            ColumnNameValues.DEBIT: 10000,
            ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
            TransactionRegistryColNameValues.SOURCE_VOLUME: 100,
            ColumnNameValues.REALIZED_PNL: 50,
            ColumnNameValues.REALIZED_PNL_EQ: 50,
            ColumnNameValues.REALIZED_PNL_FX: None,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: None,
            ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
        },
    ]
    result = _amend_row(input_row)

    assert result == expected_result
