"""Data loaders."""
from abc import abstractmethod
from enum import StrEnum
from typing import cast

import numpy as np
import pandas as pd

from pypmanager.const import CASH_AND_EQUIVALENTS
from pypmanager.error import DataError

NORMALISED_COL_NAMES_AVANZA = {
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

NORMALISED_COL_NAMES_LYSA = {
    "Date": "transaction_date",
    "Type": "transaction_type",
    "Amount": "amount",
    "Counterpart/Fund": "name",
    "Volume": "no_traded",
    "Price": "price",
}

DTYPES_MAP = {
    "account": str,
    "transaction_type": str,
    "name": str,
    "no_traded": float,
    "price": float,
    "amount": float,
    "commission": float,
    "currency": str,
    "isin_code": str,
    "pnl": float,
}


def _replace_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if row["transaction_type"] in [
        TransactionTypeValues.INTEREST,
        TransactionTypeValues.TAX,
    ]:
        return CASH_AND_EQUIVALENTS

    return cast(str, row["name"])


def _normalize_amount(row: pd.DataFrame) -> float:
    """Calculate amount if nan."""
    if np.isnan(row["amount"]):
        amount = row["no_traded"] * row["price"]
    else:
        amount = row["amount"]

    # Buy is a negative cash flow for us
    if row.transaction_type == TransactionTypeValues.BUY:
        amount = abs(amount) * -1
    else:
        amount = abs(amount)

    return cast(float, amount)


def _normalize_no_traded(row: pd.DataFrame) -> float:
    """Calculate number of units traded."""
    if row.transaction_type == TransactionTypeValues.BUY:
        no_traded = row["no_traded"]
    else:
        no_traded = abs(row["no_traded"]) * -1

    return cast(float, no_traded)


class TransactionTypeValues(StrEnum):
    """Represent transaction types."""

    BUY = "buy"
    SELL = "sell"
    INTEREST = "interest"
    TAX = "tax"


class DataLoader:
    """Base data loader."""

    df: pd.DataFrame | None = None
    df_raw: pd.DataFrame
    files: list[str]
    csv_separator: str = ";"

    def __init__(self) -> None:
        """Init class."""
        self.parse_csv()
        self.pre_process_df()
        self.filter_transactions()
        self.ensure_dot()
        self.cleanup_df()
        self.convert_data_types()
        self.finalize_data_load()

    def parse_csv(self) -> pd.DataFrame:
        """Parse CSV-files."""
        dfs = [pd.read_csv(file, sep=self.csv_separator) for file in self.files]
        self.df_raw = pd.concat(dfs, ignore_index=True)

    @abstractmethod
    def pre_process_df(self) -> None:
        """Load CSV."""

    def filter_transactions(self) -> None:
        """Filter transactions."""
        if self.df is None:
            raise DataError("No data")

        self.df = self.df.query(
            f"transaction_type == '{TransactionTypeValues.BUY}' or "
            f"transaction_type == '{TransactionTypeValues.SELL}' or "
            f"transaction_type == '{TransactionTypeValues.INTEREST}' or "
            f"transaction_type == '{TransactionTypeValues.TAX}'"
        )

    def ensure_dot(self) -> None:
        """Make sure values have dot as decimal separator."""
        if self.df is None:
            raise DataError("No data")

        df = self.df.copy()

        for col in ("no_traded", "price", "amount", "commission", "pnl"):
            if col in df.columns:
                df[col].replace(",", ".", regex=True, inplace=True)

        self.df = df

    def convert_data_types(self) -> None:
        """Convert data types."""
        if self.df is None:
            raise DataError("No data")

        df = self.df.copy()
        for key, val in DTYPES_MAP.items():
            if key in df.columns:
                try:
                    df[key] = df[key].astype(val)
                except ValueError as err:
                    raise ValueError(f"Unable to parse {key}") from err

        self.df = df

    def cleanup_df(self) -> None:
        """Cleanup dataframe."""
        if self.df is None:
            raise DataError("No data")

        df = self.df.copy()

        for col in (
            "amount",
            "no_traded",
            "price",
        ):
            if col in df.columns:
                df[col].replace(r"^-$", None, regex=True, inplace=True)

        for col in ("commission", "pnl", "isin_code"):  # Replace dashes with 0
            if col in df.columns:
                try:
                    df[col] = df[col].str.replace("-", "").replace("", 0)
                except AttributeError:
                    pass

        self.df = df

    def finalize_data_load(self) -> None:
        """Post-process."""
        if self.df is None:
            raise DataError("No data")

        df = self.df.copy()

        df["no_traded"] = df.apply(_normalize_no_traded, axis=1)
        df["amount"] = df.apply(_normalize_amount, axis=1)
        df["name"] = df.apply(_replace_name, axis=1)

        self.df = df


class LysaLoader(DataLoader):
    """Data loader for Lysa."""

    csv_separator = ","
    files = ["data/lysa-a.csv", "data/lysa-b.csv"]

    def pre_process_df(self) -> None:
        """Load CSV."""
        df = self.df_raw.rename(columns=NORMALISED_COL_NAMES_LYSA)
        df.set_index("transaction_date", inplace=True)

        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Replace buy
        for event in ("Switch buy", "Buy"):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.BUY.value
            )

        # Replace sell
        for event in ("Switch sell", "Sell"):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.SELL.value
            )

        df["commission"] = 0.0

        self.df = df


class AvanzaLoader(DataLoader):
    """Data loader for Avanza."""

    files = ["data/avanza.csv"]

    def pre_process_df(self) -> None:
        """Load CSV."""
        df = self.df_raw.rename(columns=NORMALISED_COL_NAMES_AVANZA)
        df.set_index("transaction_date", inplace=True)

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

        self.df = df


class MiscLoader(DataLoader):
    """Data loader for misc data."""

    files = ["data/other-a.csv"]

    def pre_process_df(self) -> None:
        """Load CSV."""
        df = self.df_raw
        df.set_index("transaction_date", inplace=True)

        for field in ("commission", "amount"):
            df[field] = df[field].str.replace(",", "")

        self.df = df


def load_data() -> tuple[pd.DataFrame, list[str]]:
    """Load all data."""
    df_a = AvanzaLoader().df
    df_b = LysaLoader().df
    df_c = MiscLoader().df

    all_data = cast(pd.DataFrame, pd.concat([df_a, df_b, df_c]))

    all_securities = cast(list[str], all_data.name.unique())

    return (
        all_data,
        all_securities,
    )
