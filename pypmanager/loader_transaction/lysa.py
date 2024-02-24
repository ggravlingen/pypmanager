"""Transaction loader for Lysa."""

from typing import cast

import pandas as pd

from pypmanager.loader_transaction.const import (
    ColumnNameValues,
    CSVSeparator,
    CurrencyValues,
    TransactionTypeValues,
)

from .base_loader import TransactionLoader


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if row[ColumnNameValues.TRANSACTION_TYPE] == TransactionTypeValues.FEE.value:
        return "Lysa management fee"

    return cast(str, row[ColumnNameValues.NAME])


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

    col_map = {
        "Date": ColumnNameValues.TRANSACTION_DATE,
        "Type": ColumnNameValues.TRANSACTION_TYPE,
        "Amount": ColumnNameValues.AMOUNT,
        "Counterpart/Fund": ColumnNameValues.NAME,
        "Volume": ColumnNameValues.NO_TRADED,
        "Price": ColumnNameValues.PRICE,
    }

    csv_separator = CSVSeparator.COMMA
    file_pattern = "lysa*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        df_raw = self.df_final

        df_raw[ColumnNameValues.BROKER] = "Lysa"
        df_raw[ColumnNameValues.NAME] = df_raw.apply(_replace_fee_name, axis=1)

        df_raw[ColumnNameValues.COMMISSION] = None
        df_raw[ColumnNameValues.CURRENCY] = CurrencyValues.SEK

        self.df_final = df_raw
