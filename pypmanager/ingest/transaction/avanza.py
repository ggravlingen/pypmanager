"""Transaction loader for Avanza."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base_loader import TransactionLoader
from .const import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)

if TYPE_CHECKING:
    import pandas as pd


def _transaction_type(row: pd.DataFrame) -> pd.Series:
    """Handle special cases."""
    if (
        row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE] == "Övrigt"
        and row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY]
        == "Avkastningsskatt"
    ):
        return TransactionTypeValues.FEE

    if (
        row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE] == "Övrigt"
        and "Flyttavg" in row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY]
    ):
        return TransactionTypeValues.FEE_CREDIT

    return row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE]


class AvanzaLoader(TransactionLoader):
    """Data loader for Avanza."""

    col_map = {  # noqa: RUF012
        "Datum": TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
        "Konto": ColumnNameValues.ACCOUNT,
        "Typ av transaktion": TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
        "Värdepapper/beskrivning": (
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY
        ),
        "Antal": TransactionRegistryColNameValues.SOURCE_VOLUME,
        "Kurs": TransactionRegistryColNameValues.SOURCE_PRICE,
        "Belopp": ColumnNameValues.AMOUNT,
        "Courtage": TransactionRegistryColNameValues.SOURCE_FEE,
        "Valuta": TransactionRegistryColNameValues.SOURCE_CURRENCY.value,
        "ISIN": TransactionRegistryColNameValues.SOURCE_ISIN,
        "FX": TransactionRegistryColNameValues.SOURCE_FX.value,
    }

    file_pattern = "avanza*.csv"
    date_format_pattern = "%Y-%m-%d"

    def pre_process_df(self: AvanzaLoader) -> None:
        """Broker specific manipulation of the data frame."""
        df_raw = self.df_final

        df_raw[TransactionRegistryColNameValues.SOURCE_BROKER.value] = "Avanza"

        # We don't need this column as we calculate it in this library
        if "Resultat" in df_raw.columns:
            df_raw = df_raw.drop(columns=["Resultat"])

        df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE] = df_raw.apply(
            _transaction_type,
            axis=1,
        )

        self.df_final = df_raw
