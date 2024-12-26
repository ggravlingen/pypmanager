"""Build a dataframe what contains historical metrics for a held security."""

from __future__ import annotations

from functools import cached_property

import pandas as pd

from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.settings import Settings


class SecurityHoldingHistory:
    """Build a dataframe what contains historical metrics for a held security."""

    def __init__(self, isin_code: str, df_transaction_registry: pd.DataFrame) -> None:
        """Init class."""
        self.isin_code = isin_code

        # Filter transactions for ISIN code
        self.transaction_list = df_transaction_registry[
            df_transaction_registry[TransactionRegistryColNameValues.SOURCE_ISIN]
            == isin_code
        ]

        self.series_start_date = self.transaction_list.index.min()
        self.series_end_date = self.transaction_list.index.max()

    @cached_property
    def series_date_range(self) -> pd.Series:
        """Get the date range for the series."""
        return pd.date_range(
            self.series_start_date,
            self.series_end_date,
            freq="B",
            tz=Settings.system_time_zone,
        )
