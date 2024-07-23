"""Transaction loader for Lysa."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base_loader import TransactionLoader
from .const import (
    ColumnNameValues,
    CSVSeparator,
    CurrencyValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)

if TYPE_CHECKING:
    import pandas as pd


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if (
        row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE]
        == TransactionTypeValues.FEE.value
    ):
        return "Lysa management fee"

    return cast(str, row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY])


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

    col_map = {  # noqa: RUF012
        "Date": TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
        "Type": TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
        "Amount": ColumnNameValues.AMOUNT,
        "Counterpart/Fund": TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
        "Volume": TransactionRegistryColNameValues.SOURCE_VOLUME,
        "Price": TransactionRegistryColNameValues.SOURCE_PRICE,
    }

    csv_separator = CSVSeparator.COMMA
    file_pattern = "lysa*.csv"
    date_format_pattern = "%Y-%m-%dT%H:%M:%S.%fZ"

    def pre_process_df(self: LysaLoader) -> None:
        """Load CSV."""
        df_raw = self.df_final

        df_raw[ColumnNameValues.BROKER] = "Lysa"
        df_raw[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY] = df_raw.apply(
            _replace_fee_name, axis=1
        )

        df_raw[TransactionRegistryColNameValues.SOURCE_FEE] = None
        df_raw[ColumnNameValues.CURRENCY] = CurrencyValues.SEK

        self.df_final = df_raw
