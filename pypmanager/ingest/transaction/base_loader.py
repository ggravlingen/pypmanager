"""Base loader."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Self

import pandas as pd

from pypmanager.error import DataIntegrityError
from pypmanager.settings import Settings

from .const import (
    ColumnNameValues,
    CSVSeparator,
    TransactionRegistryColNameValues,
)

_LOGGER = logging.getLogger(__package__)

if TYPE_CHECKING:
    from types import TracebackType


def _get_filename(file_path: Path) -> str:
    """Return name of file."""
    filename = file_path.name.replace(".csv", "")
    splitted_file_path = filename.split("-")

    if len(splitted_file_path) == 2:  # noqa: PLR2004
        filename = splitted_file_path[1]
    else:
        filename = splitted_file_path[0]

    return filename.capitalize()


EMPTY_DF = pd.DataFrame(
    columns=[
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
        ColumnNameValues.ACCOUNT,
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
        TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
        TransactionRegistryColNameValues.SOURCE_VOLUME,
        TransactionRegistryColNameValues.SOURCE_PRICE,
        ColumnNameValues.AMOUNT,
        TransactionRegistryColNameValues.SOURCE_FEE,
        TransactionRegistryColNameValues.SOURCE_CURRENCY.value,
        TransactionRegistryColNameValues.SOURCE_ISIN,
    ],
)


class TransactionLoader(ABC):
    """
    Base data loader.

    The transaction loader is responsible for loading transaction data from CSV files
    and processing it into a DataFrame. It handles the loading, renaming, filtering,
    and validation of the data, as well as any broker-specific pre-processing.

    If also aggregates the data by date and calculates total amount and average price.
    """

    csv_separator: str = CSVSeparator.SEMI_COLON
    col_map: ClassVar[dict[str, str] | None] = None
    df_final: pd.DataFrame
    file_pattern: str
    date_format_pattern: str
    include_transaction_type: ClassVar[list[str] | None] = None
    """
    A list of transaction types, using the source data names, to import.

    Example: Buy, Sell.
    """
    drop_cols: ClassVar[list[str] | None] = None
    """A list of columns to drop from the data frame."""

    async def __aenter__(self) -> Self:
        """Enter context manager."""
        self.load_data_files()
        self.normalise_column_name()
        await self.async_drop_columns()
        await self.async_pre_process_df()
        await self.async_filter_transaction_type()
        self.normalize_transaction_date()
        self.validate()
        await self._async_validate_columns()
        return self

    async def __aexit__(  # noqa: B027
        self: TransactionLoader,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""

    def load_data_files(self: TransactionLoader) -> None:
        """Parse CSV-files and load them into a data frame."""
        folder_path = Path(Settings.dir_transaction_data_local)
        files = list(Path.glob(folder_path, self.file_pattern))

        dfs: list[pd.DataFrame] = []
        for file in files:
            df_load = pd.read_csv(file, sep=self.csv_separator)
            filename = _get_filename(file)
            df_load[TransactionRegistryColNameValues.SOURCE_FILE.value] = filename

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

    async def async_drop_columns(self: TransactionLoader) -> None:
        """Drop columns that are not needed."""
        if self.drop_cols is None:
            return

        df_raw = self.df_final.copy()

        for drop_col in self.drop_cols:
            if drop_col in df_raw.columns:
                df_raw = df_raw.drop(columns=drop_col)

        self.df_final = df_raw

    def normalise_column_name(self: TransactionLoader) -> None:
        """Set index."""
        df_raw = self.df_final.copy()

        if self.col_map is not None:
            df_raw = df_raw.rename(columns=self.col_map)

        self.df_final = df_raw

    async def async_filter_transaction_type(self: TransactionLoader) -> None:
        """Filter transaction types."""
        if self.include_transaction_type is None:
            return

        df_raw = self.df_final.copy()

        df_raw = df_raw[
            df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE].isin(
                self.include_transaction_type
            )
        ]

        self.df_final = df_raw

    def normalize_transaction_date(self: TransactionLoader) -> None:
        """
        Make sure transaction date is in the correct format.

        We expect 2024-06-27 00:00:00+02:00.
        """
        df_raw = self.df_final

        df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE] = (
            pd.to_datetime(
                df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE],
                format=self.date_format_pattern,
            )
        )

        self.df_final = df_raw

    def validate(self: TransactionLoader) -> None:
        """Validate the data frame."""
        if (
            TransactionRegistryColNameValues.SOURCE_ISIN.value
            not in self.df_final.columns
        ):
            msg = f"ISIN column is missing in {self.file_pattern}"
            _LOGGER.error(msg)

    async def _async_validate_columns(self: TransactionLoader) -> None:
        """
        Validate columns.

        Makes sure the final data frame has the expected columns.
        """
        expected_columns = [
            ColumnNameValues.AMOUNT,
            TransactionRegistryColNameValues.SOURCE_ACCOUNT_NAME,
            TransactionRegistryColNameValues.SOURCE_BROKER,
            TransactionRegistryColNameValues.SOURCE_CURRENCY,
            TransactionRegistryColNameValues.SOURCE_FEE,
            TransactionRegistryColNameValues.SOURCE_FILE,
            TransactionRegistryColNameValues.SOURCE_FX,
            TransactionRegistryColNameValues.SOURCE_ISIN,
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
            TransactionRegistryColNameValues.SOURCE_PRICE,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
            TransactionRegistryColNameValues.SOURCE_VOLUME,
        ]

        actual_columns = self.df_final.columns.tolist()

        # Find columns that are in actual_columns but not in expected_columns
        missing_columns = set(expected_columns) - set(actual_columns)
        extra_columns = set(actual_columns) - set(expected_columns)

        if missing_columns:
            msg = f"Missing columns: {missing_columns}. In {self.__class__.__name__}."
            raise DataIntegrityError(msg)

        if extra_columns:
            msg = f"Extra columns found: {extra_columns}. In {self.__class__.__name__}."
            raise DataIntegrityError(msg)

    @abstractmethod
    async def async_pre_process_df(self: TransactionLoader) -> None:
        """Broker specific manipulation of the data frame."""
