"""Base loader."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pandas as pd

from pypmanager.settings import Settings

from .const import (
    ColumnNameValues,
    CSVSeparator,
    TransactionTypeValues,
)

if TYPE_CHECKING:
    from datetime import datetime


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
        msg = f"Unable to parse {value}"
        raise ValueError(msg) from err


def _get_filename(file_path: Path) -> str:
    """Return name of file."""
    filename = file_path.resolve().name.replace(".csv", "")
    splitted_file_path = filename.split("-")

    if len(splitted_file_path) == 2:  # noqa: PLR2004
        filename = splitted_file_path[1]
    else:
        filename = splitted_file_path[0]

    return filename.capitalize()


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
    ],
)


class TransactionLoader(ABC):
    """Base data loader."""

    csv_separator: str = CSVSeparator.SEMI_COLON
    col_map: dict[str, str] | None = None
    df_final: pd.DataFrame
    file_pattern: str
    date_format_pattern: str

    def __init__(self: TransactionLoader, report_date: datetime | None = None) -> None:
        """Init class."""
        self.report_date = report_date

        # The order is important here
        self.load_data_files()
        self.rename_and_filter()
        self.pre_process_df()
        self.normalize_transaction_date()

    def load_data_files(self: TransactionLoader) -> None:
        """Parse CSV-files and load them into a data frame."""
        folder_path = Path(Settings.dir_data)
        files = list(Path.glob(folder_path, self.file_pattern))

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
        df_raw = df_raw.map(lambda x: x.strip() if isinstance(x, str) else x)

        self.df_final = df_raw

    def rename_and_filter(self: TransactionLoader) -> None:
        """Set index."""
        df_raw = self.df_final.copy()

        if self.col_map is not None:
            df_raw = df_raw.rename(columns=self.col_map)

        if self.report_date is not None:
            df_raw = df_raw.query(f"index <= '{self.report_date}'")

        self.df_final = df_raw

    def normalize_transaction_date(self: TransactionLoader) -> None:
        """Make sure transaction date is in the correct format."""
        df_raw = self.df_final

        df_raw[ColumnNameValues.TRANSACTION_DATE] = pd.to_datetime(
            df_raw[ColumnNameValues.TRANSACTION_DATE],
            format=self.date_format_pattern,
        )

        self.df_final = df_raw

    @abstractmethod
    def pre_process_df(self: TransactionLoader) -> None:
        """Broker specific manipulation of the data frame."""
