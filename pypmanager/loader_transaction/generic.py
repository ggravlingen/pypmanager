"""Transaction loader for Misc transactions."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pypmanager.loader_transaction.const import ColumnNameValues

from .base_loader import TransactionLoader

if TYPE_CHECKING:
    import pandas as pd


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if (
        row[ColumnNameValues.TRANSACTION_TYPE] == "Plattformsavgift"
        and row[ColumnNameValues.BROKER] == "SAVR"
    ):
        return "SAVR management fee"

    return cast(str, row[ColumnNameValues.NAME])


class GenericLoader(TransactionLoader):
    """Data loader for misc data."""

    file_pattern = "other*.csv"

    def pre_process_df(self: GenericLoader) -> None:
        """Load CSV."""
        df_raw = self.df_final

        df_raw[ColumnNameValues.NAME] = df_raw.apply(_replace_fee_name, axis=1)

        self.df_final = df_raw
