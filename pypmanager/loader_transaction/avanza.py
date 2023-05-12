"""Transaction loader for Avanza."""

import pandas as pd

from pypmanager.loader_transaction.const import AccountNameValues, TransactionTypeValues

from .base_loader import TransactionLoader


def _calculate_credit(row: pd.DataFrame) -> str | None:
    """Calculate what account to credit."""
    transaction_type = row["transaction_type"]
    if transaction_type in [
        TransactionTypeValues.BUY.value,
        TransactionTypeValues.FEE.value,
        TransactionTypeValues.TAX.value,
    ]:
        return AccountNameValues.CASH

    if transaction_type == TransactionTypeValues.SELL.value:
        return AccountNameValues.MUTUAL_FUND

    return None


def _calculate_debit(row: pd.DataFrame) -> str | None:
    """Calculate what account to debit."""
    transaction_type = row["transaction_type"]
    if transaction_type in [
        TransactionTypeValues.DEPOSIT.value,
        TransactionTypeValues.SELL.value,
        TransactionTypeValues.INTEREST.value,
    ]:
        return AccountNameValues.CASH

    if transaction_type == TransactionTypeValues.TAX.value:
        return None

    return AccountNameValues.MUTUAL_FUND


class AvanzaLoader(TransactionLoader):
    """Data loader for Avanza."""

    broker_name = "Avanza"

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
        df_raw = self.df_raw

        # We don't need this column as we calculate it in this library
        df_raw = df_raw.drop(columns=["pnl"])

        self.df_raw = df_raw

    def assign_debit_credit(self) -> None:
        """Calculate what accounts are debited and credited."""
        df_raw = self.df_raw.copy()

        df_raw["debit"] = df_raw.apply(_calculate_debit, axis=1)
        df_raw["credit"] = df_raw.apply(_calculate_credit, axis=1)

        self.df_raw = df_raw

    def calculate_cash_balance(self) -> None:
        """Calculate what accounts are debited and credited."""
