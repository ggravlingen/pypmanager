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
        # (
        #     {
        #         ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
        #         ColumnNameValues.AMOUNT: 100,
        #     },
        #     [
        #         # Credit row
        #         {
        #             ColumnNameValues.AMOUNT: 100,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.SECURITIES,
        #             ColumnNameValues.CREDIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.SELL,
        #         },
        #         # Debit row
        #         {
        #             ColumnNameValues.AMOUNT: None,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
        #             ColumnNameValues.DEBIT: 100,
        #             ColumnNameValues.TRANSACTION_TYPE: None,
        #         },
        #     ],
        # ),
        # Test case for FEE transaction
        (
            {
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.FEE,
                ColumnNameValues.AMOUNT: -100,
            },
            [
                # Credit row
                {
                    ColumnNameValues.AMOUNT: -100,
                    ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
                    ColumnNameValues.CREDIT: -100,
                    ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.FEE,
                },
                # Debit row
                {
                    ColumnNameValues.AMOUNT: None,
                    ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
                    ColumnNameValues.DEBIT: -100,
                    ColumnNameValues.TRANSACTION_TYPE: None,
                },
            ],
        ),
        # # Test case for TAX transaction
        # (
        #     {
        #         ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.TAX,
        #         ColumnNameValues.AMOUNT: -100,
        #     },
        #     [
        #         # Credit row
        #         {
        #             ColumnNameValues.AMOUNT: -100,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
        #             ColumnNameValues.CREDIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.TAX,
        #         },
        #         # Debit row
        #         {
        #             ColumnNameValues.AMOUNT: None,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
        #             ColumnNameValues.DEBIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: None,
        #         },
        #     ],
        # ),
        # # Test case for DEPOSIT transaction
        # (
        #     {
        #         ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.DEPOSIT,
        #         ColumnNameValues.AMOUNT: 100,
        #     },
        #     [
        #         # Credit row
        #         {
        #             ColumnNameValues.AMOUNT: 100,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
        #             ColumnNameValues.CREDIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.DEPOSIT,
        #         },
        #         # Debit row
        #         {
        #             ColumnNameValues.AMOUNT: None,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
        #             ColumnNameValues.DEBIT: 100,
        #             ColumnNameValues.TRANSACTION_TYPE: None,
        #         },
        #     ],
        # ),
        # # Test case for DIVIDEND transaction
        # (
        #     {
        #         ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.DIVIDEND,
        #         ColumnNameValues.AMOUNT: 100,
        #     },
        #     [
        #         # Credit row
        #         {
        #             ColumnNameValues.AMOUNT: 100,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
        #             ColumnNameValues.CREDIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.DIVIDEND,
        #         },
        #         # Debit row
        #         {
        #             ColumnNameValues.AMOUNT: None,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
        #             ColumnNameValues.DEBIT: 100,
        #             ColumnNameValues.TRANSACTION_TYPE: None,
        #         },
        #     ],
        # ),
        # # Test case for CASHBACK transaction
        # (
        #     {
        #         ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.CASHBACK,
        #         ColumnNameValues.AMOUNT: 100,
        #     },
        #     [
        #         # Credit row
        #         {
        #             ColumnNameValues.AMOUNT: 100,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
        #             ColumnNameValues.CREDIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.CASHBACK,
        #         },
        #         # Debit row
        #         {
        #             ColumnNameValues.AMOUNT: None,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
        #             ColumnNameValues.DEBIT: 100,
        #             ColumnNameValues.TRANSACTION_TYPE: None,
        #         },
        #     ],
        # ),
        # # Test case for INTEREST transaction
        # (
        #     {
        #         ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
        #         ColumnNameValues.AMOUNT: 100,
        #     },
        #     [
        #         # Credit row
        #         {
        #             ColumnNameValues.AMOUNT: 100,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.EQUITY,
        #             ColumnNameValues.CREDIT: -100,
        #             ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
        #         },
        #         # Debit row
        #         {
        #             ColumnNameValues.AMOUNT: None,
        #             ColumnNameValues.ACCOUNT: AccountNameValues.CASH,
        #             ColumnNameValues.DEBIT: 100,
        #             ColumnNameValues.TRANSACTION_TYPE: None,
        #         },
        #     ],
        # ),
    ],
)
def test_amend_row(row, expected_result) -> None:
    """Test function _amend_row."""
    result = _amend_row(row)
    from pprint import pprint

    pprint(result)
    assert result == expected_result
