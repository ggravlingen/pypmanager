"""Class to create a general ledger."""
from typing import Any

import pandas as pd

from .calculate_aggregates import calculate_results
from .const import AccountNameValues, ColumnNameValues, TransactionTypeValues


def _amend_row(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Amend row."""
    debit_row = row.copy()
    credit_row = row.copy()

    ledger_list: list[dict[str, Any]] = []

    amount = debit_row[ColumnNameValues.AMOUNT]
    transaction_type = debit_row[ColumnNameValues.TRANSACTION_TYPE]

    if transaction_type == TransactionTypeValues.BUY:
        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        credit_row[ColumnNameValues.CREDIT] = amount

        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.SECURITIES
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.DEBIT] = -amount
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

    if transaction_type == TransactionTypeValues.SELL:
        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.SECURITIES
        credit_row[ColumnNameValues.CREDIT] = -amount

        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.DEBIT] = amount
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

    if transaction_type in [TransactionTypeValues.FEE, TransactionTypeValues.TAX]:
        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        credit_row[ColumnNameValues.CREDIT] = amount

        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.DEBIT] = amount
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

    if transaction_type in [
        TransactionTypeValues.DEPOSIT,
        TransactionTypeValues.DIVIDEND,
        TransactionTypeValues.CASHBACK,
        TransactionTypeValues.INTEREST,
    ]:
        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
        credit_row[ColumnNameValues.CREDIT] = -amount

        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.DEBIT] = amount
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

    ledger_list.append(credit_row)
    ledger_list.append(debit_row)

    return ledger_list


class GeneralLedger:
    """General ledger."""

    ledger_list: list[dict[str, Any]]
    ledger_df: pd.DataFrame
    output_df: pd.DataFrame

    def __init__(self, transactions: pd.DataFrame) -> None:
        """Init."""
        self.transactions = calculate_results(transactions)

        self.transactions_to_dict()
        self.create_ledger()

    def transactions_to_dict(self) -> None:
        """Convert transactions to dict."""
        self.ledger_list = self.transactions.reset_index().to_dict(orient="records")

    def create_ledger(self) -> None:
        """Create ledger."""
        ledger_list: list[dict[str, Any]] = []
        for row in self.ledger_list:
            ledger_list.extend(_amend_row(row=row))

        self.output_df = pd.DataFrame(ledger_list).set_index(
            ColumnNameValues.TRANSACTION_DATE
        )
