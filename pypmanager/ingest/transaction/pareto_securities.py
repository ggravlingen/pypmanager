"""Transaction loader for Misc transactions."""

from __future__ import annotations

from typing import ClassVar

from .base_loader import TransactionLoader
from .const import (
    ColumnNameValues,
    CSVSeparator,
    TransactionRegistryColNameValues,
)


class ParetoSecuritiesLoader(TransactionLoader):
    """
    Data loader Pareto Securities.

    Has the following columns:
    ISIN,
    Affärsdag
    Likviddag
    Ticker
    Transaktionstyp
    Antal
    Kurs
    Belopp
    Valuta
    Avräkningsnota
    Totalt
    Courtage
    exportToCsv_contractnotes_header_valRate
    exportToCsv_contractnotes_header_documentId
    exportToCsv_contractnotes_header_downloadHash
    exportToCsv_contractnotes_header_rowId
    exportToCsv_contractnotes_header_hashSum
    """

    csv_separator = CSVSeparator.COMMA

    col_map: ClassVar = {
        "ISIN": TransactionRegistryColNameValues.SOURCE_ISIN,
        "Affärsdag": TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
        "Ticker": TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
        "Transaktionstyp": TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
        "Antal": TransactionRegistryColNameValues.SOURCE_VOLUME,
        "Courtage": TransactionRegistryColNameValues.SOURCE_FEE,
        "Kurs": TransactionRegistryColNameValues.SOURCE_PRICE,
        "Totalt": ColumnNameValues.AMOUNT,
        "Valuta": TransactionRegistryColNameValues.SOURCE_CURRENCY,
    }

    file_pattern = "pareto*.csv"
    date_format_pattern = "%Y-%m-%d"

    include_transaction_type: ClassVar = [
        "Buy",
        "Sell",
    ]

    drop_cols: ClassVar = [
        "Likviddag",
        "Ticker",
        "Belopp",
        "Avräkningsnota",
        "exportToCsv_contractnotes_header_valRate",
        "exportToCsv_contractnotes_header_documentId",
        "exportToCsv_contractnotes_header_downloadHash",
        "exportToCsv_contractnotes_header_rowId",
        "exportToCsv_contractnotes_header_hashSum",
    ]

    async def async_pre_process_df(self: ParetoSecuritiesLoader) -> None:
        """Load CSV."""
        df_raw = self.df_final

        df_raw[TransactionRegistryColNameValues.SOURCE_BROKER.value] = "Pareto"

        self.df_final = df_raw
