"""Transaction loader for Avanza."""

from __future__ import annotations

from typing import ClassVar

import pandas as pd

from .base_loader import TransactionLoader
from .const import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)


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
        "Konto": TransactionRegistryColNameValues.SOURCE_ACCOUNT_NAME,
        "Typ av transaktion": TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
        "Värdepapper/beskrivning": (
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY
        ),
        "Antal": TransactionRegistryColNameValues.SOURCE_VOLUME,
        "Kurs": TransactionRegistryColNameValues.SOURCE_PRICE,
        "Belopp": ColumnNameValues.AMOUNT,
        "Courtage": TransactionRegistryColNameValues.SOURCE_FEE,
        "Courtage (SEK)": TransactionRegistryColNameValues.SOURCE_FEE,
        "Valuta": TransactionRegistryColNameValues.SOURCE_CURRENCY.value,
        "Instrumentvaluta": TransactionRegistryColNameValues.SOURCE_CURRENCY.value,
        "Transaktionsvaluta": (
            TransactionRegistryColNameValues.SOURCE_CURRENCY_NOMINAL.value
        ),
        "ISIN": TransactionRegistryColNameValues.SOURCE_ISIN,
        "FX": TransactionRegistryColNameValues.SOURCE_FX.value,
        "Valutakurs": TransactionRegistryColNameValues.SOURCE_FX.value,
    }

    file_pattern = "avanza*.csv"
    date_format_pattern = "%Y-%m-%d"

    include_transaction_type: ClassVar = [
        "Köp",
        "Sälj",
        "Utdelning",
        "Ränta",
        "Övrigt",
    ]

    drop_cols: ClassVar = [
        "Resultat",
        TransactionRegistryColNameValues.SOURCE_CURRENCY_NOMINAL.value,
    ]

    async def async_pre_process_df(self: AvanzaLoader) -> None:
        """Broker specific manipulation of the data frame."""
        df_raw = self.df_final

        df_raw[TransactionRegistryColNameValues.SOURCE_BROKER.value] = "Avanza"

        df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE] = df_raw.apply(
            _transaction_type,
            axis=1,
        )

        # Merge columns with the same name and keep the value that is not NaN
        with pd.option_context("future.no_silent_downcasting", True):  # noqa: FBT003
            df_raw = df_raw.T.groupby(level=0).apply(lambda x: x.bfill().iloc[0]).T

        self.df_final = df_raw
