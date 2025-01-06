"""Base loader."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Self

import pandas as pd

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
    """Base data loader."""

    csv_separator: str = CSVSeparator.SEMI_COLON
    col_map: dict[str, str] | None = None
    df_final: pd.DataFrame
    file_pattern: str
    date_format_pattern: str

    async def __aenter__(self) -> Self:
        """Enter context manager."""
        self.load_data_files()
        self.rename_and_filter()
        await self.async_pre_process_df()
        self.normalize_transaction_date()
        self.validate()
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
        folder_path = Path(Settings.dir_transaction_data)
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

    def rename_and_filter(self: TransactionLoader) -> None:
        """Set index."""
        df_raw = self.df_final.copy()

        if self.col_map is not None:
            df_raw = df_raw.rename(columns=self.col_map)

        self.df_final = df_raw

    def normalize_transaction_date(self: TransactionLoader) -> None:
        """Make sure transaction date is in the correct format."""
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

    @abstractmethod
    async def async_pre_process_df(self: TransactionLoader) -> None:
        """Broker specific manipulation of the data frame."""
