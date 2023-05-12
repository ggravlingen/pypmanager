"""Transaction loader for Lysa."""
from typing import cast

import pandas as pd

from pypmanager.loader_transaction.const import (
    AccountNameValues,
    CurrencyValues,
    TransactionTypeValues,
)

from .base_loader import TransactionLoader
from .const import LOGGER


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if row["transaction_type"] == TransactionTypeValues.FEE.value:
        return "Lysa management fee"

    return cast(str, row["name"])


def _calculate_credit(row: pd.DataFrame) -> str | None:
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


def _calculate_debit(row: pd.DataFrame) -> str | None:
    """Calculate what account to debit."""
    if row["transaction_type"] in [
        TransactionTypeValues.DEPOSIT.value,
        TransactionTypeValues.SELL.value,
        TransactionTypeValues.FEE.value,
    ]:
        return AccountNameValues.CASH

    return AccountNameValues.MUTUAL_FUND


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

    broker_name = "Lysa"

    col_map = {
        "Date": "transaction_date",
        "Type": "transaction_type",
        "Amount": "amount",
        "Counterpart/Fund": "name",
        "Volume": "no_traded",
        "Price": "price",
    }

    csv_separator = ","
    file_pattern = "lysa*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        df_raw = self.df_raw

        df_raw["name"] = df_raw.apply(_replace_fee_name, axis=1)

        df_raw["commission"] = None
        df_raw["currency"] = CurrencyValues.SEK
        df_raw["account"] = self.broker_name

        self.df_raw = df_raw

    def calculate_cash_balance(self) -> None:
        """Calculate cash balance."""
        df_raw = self.df_final.copy()

        debit_sum = df_raw.loc[
            df_raw["debit"] == AccountNameValues.CASH, "amount"
        ].sum()

        credit_sum = df_raw.loc[
            df_raw["credit"] == AccountNameValues.CASH, "amount"
        ].sum()

        total_amount = debit_sum + credit_sum

        LOGGER.debug(f"Inserting Lysa cash position: {round(total_amount, 4)}")

        new_row = {
            "account": "lysa",
            "transaction_type": TransactionTypeValues.CASH,
            "name": "Cash and equivalents - Lysa",
            "amount": total_amount,
            "no_traded": total_amount,
            "price": 1,
            "currency": "SEK",
            "broker": "lysa",
        }

        df_raw_copy = df_raw.copy()

        # Insert the new row using loc
        df_raw_copy.loc[len(df_raw)] = new_row

        self.df_final = df_raw_copy

    def assign_debit_credit(self) -> None:
        """Calculate what accounts are debited and credited."""
        df_raw = self.df_final.copy()

        df_raw["debit"] = df_raw.apply(_calculate_debit, axis=1)
        df_raw["credit"] = df_raw.apply(_calculate_credit, axis=1)

        self.df_final = df_raw
