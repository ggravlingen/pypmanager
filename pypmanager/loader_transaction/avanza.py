"""Transaction loader for Avanza."""
import pandas as pd

from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues

from .base_loader import TransactionLoader


def _transaction_type(row: pd.DataFrame) -> pd.Series:
    """Handle special cases."""
    if (
        row[ColumnNameValues.TRANSACTION_TYPE] == "Övrigt"
        and row[ColumnNameValues.NAME] == "Avkastningsskatt"
    ):
        return TransactionTypeValues.FEE

    if (
        row[ColumnNameValues.TRANSACTION_TYPE] == "Övrigt"
        and "Flyttavg" in row[ColumnNameValues.NAME]
    ):
        return TransactionTypeValues.FEE_CREDIT

    return row[ColumnNameValues.TRANSACTION_TYPE]


class AvanzaLoader(TransactionLoader):
    """Data loader for Avanza."""

    col_map = {
        "Datum": ColumnNameValues.TRANSACTION_DATE,
        "Konto": ColumnNameValues.ACCOUNT,
        "Typ av transaktion": ColumnNameValues.TRANSACTION_TYPE,
        "Värdepapper/beskrivning": ColumnNameValues.NAME,
        "Antal": ColumnNameValues.NO_TRADED,
        "Kurs": ColumnNameValues.PRICE,
        "Belopp": ColumnNameValues.AMOUNT,
        "Courtage": ColumnNameValues.COMMISSION,
        "Valuta": ColumnNameValues.CURRENCY,
        "ISIN": ColumnNameValues.ISIN_CODE,
        "FX": ColumnNameValues.FX,
    }

    file_pattern = "avanza*.csv"

    def pre_process_df(self) -> None:
        """Broker specific manipulation of the data frame."""
        df_raw = self.df_final

        df_raw[ColumnNameValues.BROKER] = "Avanza"

        # We don't need this column as we calculate it in this library
        if "Resultat" in df_raw.columns:
            df_raw = df_raw.drop(columns=["Resultat"])

        df_raw[ColumnNameValues.TRANSACTION_TYPE] = df_raw.apply(
            _transaction_type, axis=1
        )

        self.df_final = df_raw
