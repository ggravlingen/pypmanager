"""Transaction loader for Misc transactions."""

from typing import cast

import pandas as pd

from .base_loader import TransactionLoader


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if row["transaction_type"] == "Plattformsavgift":
        return "SAVR management fee"

    return cast(str, row["name"])


class MiscLoader(TransactionLoader):
    """Data loader for misc data."""

    file_pattern = "other*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        df_raw = self.df_raw

        df_raw["name"] = df_raw.apply(_replace_fee_name, axis=1)

        self.df_raw = df_raw
