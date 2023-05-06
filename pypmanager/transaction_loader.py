"""Data loaders."""
from abc import abstractmethod
from datetime import datetime
from enum import StrEnum
import glob
import os
from typing import cast

import numpy as np
import pandas as pd

from pypmanager.const import CASH_AND_EQUIVALENTS
from pypmanager.error import DataError
from pypmanager.settings import Settings

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

NUMBER_COLS = [
    "no_traded",
    "price",
    "amount",
    "commission",
    "pnl",
]


class TransactionTypeValues(StrEnum):
    """Represent transaction types."""

    BUY = "buy"
    SELL = "sell"
    INTEREST = "interest"
    TAX = "tax"


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


def _cleanup_number(value: str) -> float | None:
    """Make sure values are converted to floats."""
    if (value := f"{value}") == "-":
        return 0

    value = value.replace(",", ".")
    value = value.replace(" ", "")

    try:
        return float(value)
    except ValueError as err:
        raise ValueError(f"Unable to parse {value}") from err


class TransactionLoader:
    """Base data loader."""

    csv_separator: str = ";"
    col_map: dict[str, str] | None = None
    df: pd.DataFrame | None = None
    df_raw: pd.DataFrame
    file_pattern: str

    def __init__(self, report_date: datetime | None = None) -> None:
        """Init class."""
        self.report_date = report_date

        self.parse_csv()
        self.pre_process_df()
        self.filter_transactions()
        self.cleanup_df()
        self.convert_data_types()
        self.finalize_data_load()

    def rename_set_index_filter(self) -> None:
        """Set index."""
        df = self.df_raw

        if self.col_map is not None:
            df.rename(columns=self.col_map, inplace=True)

        df.set_index("transaction_date", inplace=True)

        if self.report_date is not None:
            df = df.query(f"index <= '{self.report_date}'")

        self.df_raw = df

    def parse_csv(self) -> pd.DataFrame:
        """Parse CSV-files."""
        files = glob.glob(os.path.join(Settings.DIR_DATA, self.file_pattern))

        dfs = [pd.read_csv(file, sep=self.csv_separator) for file in files]
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

        for col in NUMBER_COLS:
            if col in df.columns:
                df[col] = df.apply(lambda x, _col=col: _cleanup_number(x[_col]), axis=1)

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


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

    col_map = {
        "Date": "transaction_date",
        "Type": "transaction_type",
        "Amount": "amount",
        "Counterpart/Fund": "name",
        "Volume": "no_traded",
        "Price": "price",
    }

    csv_separator = ","
    file_pattern = "lysa*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        self.rename_set_index_filter()
        df = self.df_raw

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
        """Load CSV."""
        self.rename_set_index_filter()
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

        self.df = df


class MiscLoader(TransactionLoader):
    """Data loader for misc data."""

    file_pattern = "other*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        self.rename_set_index_filter()
        df = self.df_raw

        self.df = df


def load_data(report_date: datetime | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Load all data."""
    df_a = AvanzaLoader(report_date).df
    df_b = LysaLoader(report_date).df
    df_c = MiscLoader(report_date).df

    all_data = cast(pd.DataFrame, pd.concat([df_a, df_b, df_c]))

    all_securities = cast(list[str], all_data.name.unique())

    return (
        all_data,
        all_securities,
    )
