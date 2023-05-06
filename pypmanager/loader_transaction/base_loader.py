"""Base loader."""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
import glob
import os
from typing import cast

import numpy as np
import pandas as pd

from pypmanager.const import CASH_AND_EQUIVALENTS
from pypmanager.error import DataError
from pypmanager.settings import Settings

from .const import DTYPES_MAP, NUMBER_COLS, TransactionTypeValues


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
