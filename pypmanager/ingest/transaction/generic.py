"""Transaction loader for Misc transactions."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base_loader import TransactionLoader
from .const import TransactionRegistryColNameValues

if TYPE_CHECKING:
    import pandas as pd


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if (
        row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE]
        == "Plattformsavgift"
        and row[TransactionRegistryColNameValues.SOURCE_BROKER.value] == "SAVR"
    ):
        return "SAVR management fee"

    return cast(str, row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY])


class GenericLoader(TransactionLoader):
    """Data loader for misc data."""

    file_pattern = "other*.csv"
    date_format_pattern = "%Y-%m-%d"

    def pre_process_df(self: GenericLoader) -> None:
        """Load CSV."""
        df_raw = self.df_final

        df_raw[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY] = df_raw.apply(
            _replace_fee_name, axis=1
        )

        self.df_final = df_raw
