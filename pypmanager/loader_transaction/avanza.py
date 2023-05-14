"""Transaction loader for Avanza."""
import pandas as pd

from .base_loader import TransactionLoader


def _transaction_type(row: pd.DataFrame) -> pd.Series:
    """Handle special cases."""
    if row["transaction_type"] == "Övrigt" and row["name"] == "Avkastningsskatt":
        return "fee"

    if row["transaction_type"] == "Övrigt" and "Flyttavg" in row["name"]:
        return "fee"

    return row["transaction_type"]


class AvanzaLoader(TransactionLoader):
    """Data loader for Avanza."""

    col_map = {
        "Datum": "transaction_date",
        "Konto": "account",
        "Typ av transaktion": "transaction_type",
        "Värdepapper/beskrivning": "name",
        "Antal": "no_traded",
        "Kurs": "price",
        "Belopp": "amount",
        "Courtage": "commission",
        "Valuta": "currency",
        "ISIN": "isin_code",
        "Resultat": "pnl",
    }

    file_pattern = "avanza*.csv"

    def pre_process_df(self) -> None:
        """Broker specific manipulation of the data frame."""
        df_raw = self.df_final

        df_raw["broker"] = "Avanza"

        # We don't need this column as we calculate it in this library
        if "pnl" in df_raw.columns:
            df_raw = df_raw.drop(columns=["pnl"])

        df_raw["transaction_type"] = df_raw.apply(_transaction_type, axis=1)

        self.df_final = df_raw
