"""Transaction loader for Avanza."""


from .base_loader import TransactionLoader


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

        # We don't need this column as we calculate it in this library
        if "pnl" in df_raw.columns:
            df_raw = df_raw.drop(columns=["pnl"])

        self.df_final = df_raw
