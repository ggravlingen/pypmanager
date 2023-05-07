"""Base loader."""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
import glob
import os
import random
from typing import cast

import numpy as np
import pandas as pd

from pypmanager.settings import Settings

from .const import DTYPES_MAP, NUMBER_COLS, TransactionTypeValues

CASH_AND_EQUIVALENTS = "Cash and equivalents"

FILTER_STATEMENT = (
    f"('{TransactionTypeValues.DIVIDEND}'"
    f",'{TransactionTypeValues.FEE}'"
    f",'{TransactionTypeValues.INTEREST}'"
    f",'{TransactionTypeValues.TAX}'"
    f",'{TransactionTypeValues.BUY}'"
    f",'{TransactionTypeValues.SELL}',)"
)


@dataclass
class ReplaceConfig:
    """Configuration to replace values."""

    search: list[str]
    target: str


REPLACE_CONFIG = [
    ReplaceConfig(
        search=["Köp", "Switch buy", "Buy"],
        target=TransactionTypeValues.BUY.value,
    ),
    ReplaceConfig(
        search=["Sälj", "Switch sell", "Sell"],
        target=TransactionTypeValues.SELL.value,
    ),
    ReplaceConfig(
        search=["Räntor"],
        target=TransactionTypeValues.INTEREST.value,
    ),
    ReplaceConfig(
        search=["Preliminärskatt"],
        target=TransactionTypeValues.TAX.value,
    ),
    ReplaceConfig(
        search=["Utdelning"],
        target=TransactionTypeValues.DIVIDEND.value,
    ),
    ReplaceConfig(
        search=["Fee"],
        target=TransactionTypeValues.FEE.value,
    ),
]


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

    # Buy and tax is a negative cash flow for us
    if row.transaction_type in [
        TransactionTypeValues.BUY,
        TransactionTypeValues.TAX,
        TransactionTypeValues.FEE,
    ]:
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

    broker_name: str | None = None
    csv_separator: str = ";"
    col_map: dict[str, str] | None = None
    df_raw: pd.DataFrame
    df_final: pd.DataFrame
    file_pattern: str

    def __init__(self, report_date: datetime | None = None) -> None:
        """Init class."""
        self.report_date = report_date

        # The order is important here
        self.load_data_files()
        self.rename_set_index_filter()
        self.pre_process_df()
        self.normalize_transaction_type()
        self.filter_transactions()
        self.cleanup_df()
        self.convert_data_types()
        self.finalize_data_load()

    def load_data_files(self) -> None:
        """Parse CSV-files and load them into a data frame."""
        files = glob.glob(os.path.join(Settings.DIR_DATA, self.file_pattern))

        dfs = [pd.read_csv(file, sep=self.csv_separator) for file in files]

        # Merge all the data frames into one
        df_raw = pd.concat(dfs, ignore_index=True)

        # Cleanup whitespace in columns
        df_raw = df_raw.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        if "broker" not in df_raw.columns and self.broker_name:
            df_raw["broker"] = self.broker_name

        self.df_raw = df_raw

    def rename_set_index_filter(self) -> None:
        """Set index."""
        df_raw = self.df_raw.copy()

        if self.col_map is not None:
            df_raw = df_raw.rename(columns=self.col_map)

        df_raw = df_raw.set_index("transaction_date")

        if self.report_date is not None:
            df_raw = df_raw.query(f"index <= '{self.report_date}'")

        # Apply randomness to time in order to have unique indices
        df_raw.index = pd.to_datetime(df_raw.index).map(
            lambda x: x.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                microsecond=random.randint(0, 999999),
            )
            if x.strftime("%Y-%m-%d") == x.strftime("%Y-%m-%d")
            else x
        )

        # Sort by transaction date
        df_raw = df_raw.sort_index()

        self.df_raw = df_raw

    @abstractmethod
    def pre_process_df(self) -> None:
        """Broker specific manipulation of the data frame."""

    def normalize_transaction_type(self) -> None:
        """
        Normalize transaction types.

        In the source data, transactions will be named differently. To enable
        calculations, we replace the names in the source data with our internal names.
        """
        df_raw = self.df_raw

        for config in REPLACE_CONFIG:
            for event in config.search:
                df_raw["transaction_type"] = df_raw["transaction_type"].replace(
                    event, config.target
                )

        self.df_raw = df_raw

    def filter_transactions(self) -> None:
        """Filter transactions."""
        df_raw = self.df_raw.copy()

        df_raw = df_raw.query(f"transaction_type in {FILTER_STATEMENT}")

        self.df_raw = df_raw

    def cleanup_df(self) -> None:
        """Cleanup dataframe."""
        df_raw = self.df_raw.copy()

        for col in NUMBER_COLS:
            if col in df_raw.columns:
                df_raw[col] = df_raw.apply(
                    lambda x, _col=col: _cleanup_number(x[_col]), axis=1
                )

        for col in ("commission", "isin_code"):  # Replace dashes with 0
            if col in df_raw.columns:
                try:
                    df_raw[col] = df_raw[col].str.replace("-", "").replace("", 0)
                except AttributeError:
                    pass

        self.df_raw = df_raw

    def convert_data_types(self) -> None:
        """Convert data types."""
        df_raw = self.df_raw.copy()

        for key, val in DTYPES_MAP.items():
            if key in df_raw.columns:
                try:
                    df_raw[key] = df_raw[key].astype(val)
                except ValueError as err:
                    raise ValueError(f"Unable to parse {key}") from err

        self.df_raw = df_raw

    def finalize_data_load(self) -> None:
        """Post-process."""
        df_raw = self.df_raw.copy()

        df_raw["no_traded"] = df_raw.apply(_normalize_no_traded, axis=1)
        df_raw["amount"] = df_raw.apply(_normalize_amount, axis=1)
        df_raw["name"] = df_raw.apply(_replace_name, axis=1)

        self.df_final = df_raw
