"""Transaction loader for Avanza."""

from .base_loader import TransactionLoader
from .const import TransactionTypeValues


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
        df = self.df_raw

        # Replace buy
        for event in ("Köp",):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.BUY.value
            )

        # Replace sell
        for event in ("Sälj",):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.SELL.value
            )

        for event in ("Räntor",):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.INTEREST.value
            )

        for event in ("Preliminärskatt",):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.TAX.value
            )

        for event in ("Utdelning",):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.DIVIDEND.value
            )

        # We don't need this column as we calculate it in this library
        df.drop(columns=["pnl"], inplace=True)

        self.df_raw = df
