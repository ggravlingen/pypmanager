"""Base loader."""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
import glob
import os
import random
from typing import cast

import pandas as pd

from pypmanager.settings import Settings

from .const import (
    DTYPES_MAP,
    NUMBER_COLS,
    ColumnNameValues,
    CSVSeparator,
    TransactionTypeValues,
)

FILTER_STATEMENT = (
    f"('{TransactionTypeValues.DIVIDEND}'"
    f",'{TransactionTypeValues.FEE}'"
    f",'{TransactionTypeValues.FEE_CREDIT}'"
    f",'{TransactionTypeValues.INTEREST}'"
    f",'{TransactionTypeValues.DEPOSIT}'"
    f",'{TransactionTypeValues.CASHBACK}'"
    f",'{TransactionTypeValues.WITHDRAW}'"
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
        search=["Fee", "Plattformsavgift"],
        target=TransactionTypeValues.FEE.value,
    ),
    ReplaceConfig(
        search=["Deposit", "Insättning"],
        target=TransactionTypeValues.DEPOSIT.value,
    ),
]


def _normalize_amount(row: pd.DataFrame) -> float:
    """Calculate amount if nan."""
    if row[ColumnNameValues.TRANSACTION_TYPE] in [
        TransactionTypeValues.CASHBACK,
        TransactionTypeValues.FEE,
    ]:
        amount = row[ColumnNameValues.AMOUNT]
    else:
        amount = row[ColumnNameValues.NO_TRADED] * row[ColumnNameValues.PRICE]

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
        no_traded = row[ColumnNameValues.NO_TRADED]
    else:
        no_traded = abs(row[ColumnNameValues.NO_TRADED]) * -1

    return cast(float, no_traded)


def _normalize_fx(row: pd.DataFrame) -> float:
    """Set FX rate to a value."""
    if ColumnNameValues.FX not in row:
        return 1.00

    if pd.isna(row[ColumnNameValues.FX]):
        return 1.00

    return cast(float, row[ColumnNameValues.FX])


def _cleanup_number(value: str | None) -> float | None:
    """Make sure values are converted to floats."""
    if value is None:
        return None

    if (value := f"{value}") == "-":
        return 0

    value = value.replace(",", ".")
    value = value.replace(" ", "")

    try:
        return float(value)
    except ValueError as err:
        raise ValueError(f"Unable to parse {value}") from err


def _get_filename(file_path: str) -> str:
    """Return name of file."""
    filename = os.path.basename(file_path).replace(".csv", "")
    splitted_file_path = filename.split("-")

    if len(splitted_file_path) == 2:
        filename = splitted_file_path[1]
    else:
        filename = splitted_file_path[0]

    filename = filename.capitalize()

    return filename


EMPTY_DF = pd.DataFrame(
    columns=[
        ColumnNameValues.TRANSACTION_DATE,
        ColumnNameValues.ACCOUNT,
        ColumnNameValues.TRANSACTION_TYPE,
        ColumnNameValues.NAME,
        ColumnNameValues.NO_TRADED,
        ColumnNameValues.PRICE,
        ColumnNameValues.AMOUNT,
        ColumnNameValues.COMMISSION,
        ColumnNameValues.CURRENCY,
        ColumnNameValues.ISIN_CODE,
    ]
)


class TransactionLoader:
    """Base data loader."""

    csv_separator: str = CSVSeparator.SEMI_COLON
    col_map: dict[str, str] | None = None
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
        self.normalize_data()

    def load_data_files(self) -> None:
        """Parse CSV-files and load them into a data frame."""
        files = glob.glob(os.path.join(Settings.DIR_DATA, self.file_pattern))

        dfs: list[pd.DataFrame] = []
        for file in files:
            df_load = pd.read_csv(file, sep=self.csv_separator)
            filename = _get_filename(file)
            df_load[ColumnNameValues.SOURCE] = filename

            dfs.append(df_load)

        if len(files) == 0:
            df_raw = EMPTY_DF
        elif len(files) == 1:
            df_raw = df_load
        else:
            df_raw = pd.concat(dfs, ignore_index=True)

        # Cleanup whitespace in columns
        df_raw = df_raw.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        self.df_final = df_raw

    def rename_set_index_filter(self) -> None:
        """Set index."""
        df_raw = self.df_final.copy()

        if self.col_map is not None:
            df_raw = df_raw.rename(columns=self.col_map)

        df_raw = df_raw.set_index(ColumnNameValues.TRANSACTION_DATE)

        if self.report_date is not None:
            df_raw = df_raw.query(f"index <= '{self.report_date}'")

        # Apply randomness to time in order to have unique indices
        df_raw.index = pd.to_datetime(df_raw.index).map(
            lambda x: x.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                microsecond=random.randint(0, 999999),
            )
            if x and x.strftime("%Y-%m-%d") == x.strftime("%Y-%m-%d")
            else x
        )

        # Sort by transaction date
        df_raw = df_raw.sort_index()

        self.df_final = df_raw

    @abstractmethod
    def pre_process_df(self) -> None:
        """Broker specific manipulation of the data frame."""

    def normalize_transaction_type(self) -> None:
        """
        Normalize transaction types.

        In the source data, transactions will be named differently. To enable
        calculations, we replace the names in the source data with our internal names.
        """
        df_raw = self.df_final

        for config in REPLACE_CONFIG:
            for event in config.search:
                df_raw[ColumnNameValues.TRANSACTION_TYPE] = df_raw[
                    ColumnNameValues.TRANSACTION_TYPE
                ].replace(event, config.target)

        self.df_final = df_raw

    def filter_transactions(self) -> None:
        """Filter transactions."""
        df_raw = self.df_final.copy()

        df_raw = df_raw.query(
            f"{ColumnNameValues.TRANSACTION_TYPE} in {FILTER_STATEMENT}"
        )

        self.df_final = df_raw

    def cleanup_df(self) -> None:
        """Cleanup dataframe."""
        df_raw = self.df_final.copy()

        for col in NUMBER_COLS:
            if col in df_raw.columns:
                df_raw[col] = df_raw.apply(
                    lambda x, _col=col: _cleanup_number(x[_col]), axis=1
                )

        for col in (
            ColumnNameValues.COMMISSION,
            ColumnNameValues.ISIN_CODE,
        ):  # Replace dashes with 0
            if col in df_raw.columns:
                try:
                    df_raw[col] = df_raw[col].str.replace("-", "").replace("", 0)
                except AttributeError:
                    pass

        self.df_final = df_raw

    def convert_data_types(self) -> None:
        """Convert data types."""
        df_raw = self.df_final.copy()

        for key, val in DTYPES_MAP.items():
            if key in df_raw.columns:
                try:
                    df_raw[key] = df_raw[key].astype(val)
                except ValueError as err:
                    raise ValueError(f"Unable to parse {key}") from err

        self.df_final = df_raw

    def normalize_data(self) -> None:
        """Post-process."""
        df_raw = self.df_final.copy()

        df_raw[ColumnNameValues.NO_TRADED] = df_raw.apply(_normalize_no_traded, axis=1)
        df_raw[ColumnNameValues.AMOUNT] = df_raw.apply(_normalize_amount, axis=1)
        df_raw[ColumnNameValues.FX] = df_raw.apply(_normalize_fx, axis=1)

        self.df_final = df_raw
