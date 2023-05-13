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
            "name": f"Cash and equivalents - {self.broker_name}",
            "amount": total_amount,
            "no_traded": total_amount,
            "price": 1,
            "currency": "SEK",
            "broker": self.broker_name,
        }

        df_raw_copy = df_raw.copy()

        df_raw_copy.loc[len(df_raw)] = new_row

        self.df_final = df_raw_copy
