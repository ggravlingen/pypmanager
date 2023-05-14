"""Transaction loader for Lysa."""
from typing import cast

import pandas as pd

from pypmanager.loader_transaction.const import (
    CurrencyValues,
    TransactionTypeValues,
)

from .base_loader import TransactionLoader


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if row["transaction_type"] == TransactionTypeValues.FEE.value:
        return "Lysa management fee"

    return cast(str, row["name"])


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

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
        df_raw = self.df_final

        df_raw["broker"] = "Lysa"
        df_raw["name"] = df_raw.apply(_replace_fee_name, axis=1)

        df_raw["commission"] = None
        df_raw["currency"] = CurrencyValues.SEK

        self.df_final = df_raw
