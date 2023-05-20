"""Tests for the general ledger."""
import pytest

from pypmanager.loader_transaction.const import (
    AccountNameValues,
    ColumnNameValues,
    TransactionTypeValues,
)
from pypmanager.loader_transaction.general_ledger import _amend_row


@pytest.mark.parametrize(
    "row, expected_result",
    [
        # Test case for BUY transaction
        (
            {
                ColumnNameValues.AMOUNT: 100,
                ColumnNameValues.AVG_PRICE: 100,
                ColumnNameValues.NO_TRADED: 100,
                ColumnNameValues.REALIZED_PNL: None,
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
            },
            [
                # Credit row
                {
                    ColumnNameValues.AMOUNT: 100,
                    ColumnNameValues.AVG_PRICE: 100,
                    ColumnNameValues.CREDIT: -100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
                    ColumnNameValues.NO_TRADED: 100,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.BUY,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.BUY,
                },
                # Debit row
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: 100,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.DEBIT: -100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.PRICE: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.BUY,
                },
            ],
        ),
        # Test case for SELL transaction
        (
            {
                ColumnNameValues.AMOUNT: 10000,
                ColumnNameValues.AVG_PRICE: 100,
                ColumnNameValues.NO_TRADED: 100,
                ColumnNameValues.REALIZED_PNL: 50,
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
            },
            [
                {
                    ColumnNameValues.AMOUNT: 10000,
                    ColumnNameValues.AVG_PRICE: 100,
                    ColumnNameValues.CREDIT: -10000,
                    ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
                    ColumnNameValues.NO_TRADED: 100,
                    ColumnNameValues.REALIZED_PNL: 50,
                    ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: 100,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.CREDIT: 50,
                    ColumnNameValues.ACCOUNT: AccountNameValues.IS_PNL,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: 100,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.CREDIT: 50,
                    ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: 100,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.DEBIT: 10000,
                    ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.SELL,
                },
            ],
        ),
        # Test case for FEE transaction
        (
            {
                ColumnNameValues.AMOUNT: -100,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.NO_TRADED: None,
                ColumnNameValues.REALIZED_PNL: -100,
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.FEE,
            },
            [
                {
                    ColumnNameValues.AMOUNT: -100,
                    ColumnNameValues.AVG_PRICE: None,
                    ColumnNameValues.CREDIT: 100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: -100,
                    ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.FEE,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: None,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.DEBIT: 100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: None,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.DEBIT: 100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.IS_FEE,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.FEE,
                },
            ],
        ),
        # Test case for INTEREST transaction
        (
            {
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
                ColumnNameValues.AMOUNT: 100,
                ColumnNameValues.AVG_PRICE: None,
                ColumnNameValues.NO_TRADED: None,
                ColumnNameValues.REALIZED_PNL: 100,
            },
            [
                {
                    ColumnNameValues.AMOUNT: 100,
                    ColumnNameValues.AVG_PRICE: None,
                    ColumnNameValues.CREDIT: 100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: 100,
                    ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.INTEREST,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: None,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.CREDIT: 100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.IS_INTEREST,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.INTEREST,
                },
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.AVG_PRICE: None,
                    ColumnNameValues.COMMISSION: None,
                    ColumnNameValues.DEBIT: 100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
                    ColumnNameValues.NO_TRADED: None,
                    ColumnNameValues.REALIZED_PNL: None,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                    ColumnNameValues.TRANSACTION_TYPE_INTERNAL: TransactionTypeValues.INTEREST,
                },
            ],
        ),
    ],
)
def test_amend_row(row, expected_result) -> None:
    """Test function _amend_row."""
    result = _amend_row(row)

    assert result == expected_result
