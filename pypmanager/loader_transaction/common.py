"""Common functions."""
import pandas as pd

from pypmanager.loader_transaction.const import (
    AccountNameValues,
    TransactionTypeValues,
)


def calculate_credit(row: pd.DataFrame) -> str | None:
    """Calculate what account to credit."""
    transaction_type = row["transaction_type"]
    if transaction_type in [
        TransactionTypeValues.BUY.value,
    ]:
        return AccountNameValues.CASH

    if transaction_type == TransactionTypeValues.SELL.value:
        return AccountNameValues.MUTUAL_FUND

    if transaction_type == TransactionTypeValues.FEE.value:
        return AccountNameValues.IS_COSTS

    return None


def calculate_debit(row: pd.DataFrame) -> str | None:
    """Calculate what account to debit."""
    if row["transaction_type"] in [
        TransactionTypeValues.DEPOSIT.value,
        TransactionTypeValues.SELL.value,
        TransactionTypeValues.FEE.value,
    ]:
        return AccountNameValues.CASH

    return AccountNameValues.MUTUAL_FUND
