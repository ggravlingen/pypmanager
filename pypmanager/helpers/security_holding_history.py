"""Build a dataframe what contains historical metrics for a held security."""

from __future__ import annotations

from functools import cached_property
from typing import ClassVar

import pandas as pd

from pypmanager.ingest.transaction.const import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
)
from pypmanager.settings import Settings


class SecurityHoldingHistory:
    """
    Build a dataframe what contains historical metrics for a held security.

    The end result is available in the method async_get_security_holding_history().
    """

    COLS_TO_DROP: ClassVar = [
        TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
        TransactionRegistryColNameValues.SOURCE_ACCOUNT_NAME,
        TransactionRegistryColNameValues.META_TRANSACTION_YEAR,
        TransactionRegistryColNameValues.CALC_PNL_TOTAL,
        TransactionRegistryColNameValues.CALC_PNL_DIVIDEND,
        TransactionRegistryColNameValues.CALC_PNL_TRADE,
        TransactionRegistryColNameValues.CASH_FLOW_GROSS_FEE_NOMINAL,
        TransactionRegistryColNameValues.CASH_FLOW_NET_FEE_NOMINAL,
        TransactionRegistryColNameValues.CALC_TURNOVER_OR_OTHER_CF,
        TransactionRegistryColNameValues.SOURCE_FILE,
        TransactionRegistryColNameValues.SOURCE_CURRENCY,
        TransactionRegistryColNameValues.SOURCE_BROKER,
        TransactionRegistryColNameValues.SOURCE_FX,
        TransactionRegistryColNameValues.SOURCE_ISIN,
        TransactionRegistryColNameValues.SOURCE_PRICE,
        TransactionRegistryColNameValues.SOURCE_FEE,
        ColumnNameValues.AMOUNT,
    ]

    df_base: pd.DataFrame
    df_base_with_transactions: pd.DataFrame
    df_transaction_clean: pd.DataFrame

    def __init__(self, isin_code: str, df_transaction_registry: pd.DataFrame) -> None:
        """Init class."""
        self.isin_code = isin_code

        # Filter transactions for ISIN code
        self.transaction_list = df_transaction_registry[
            df_transaction_registry[TransactionRegistryColNameValues.SOURCE_ISIN]
            == isin_code
        ]

        self.series_start_date = self.transaction_list.index.min()
        # Add one day to make sure we capture the last day
        self.series_end_date = self.transaction_list.index.max() + pd.Timedelta(days=1)

        self._100_create_base_df()
        self._200_merge_transaction_list()
        self._300_drop_columns()

    @cached_property
    def series_date_range(self) -> pd.Series:
        """Get the date range for the series."""
        return pd.date_range(
            self.series_start_date,
            self.series_end_date,
            tz=Settings.system_time_zone,
        )

    def _100_create_base_df(self) -> pd.DataFrame:
        """Create a base DataFrame with the date range as index."""
        self.df_base = pd.DataFrame(index=self.series_date_range)

    def _200_merge_transaction_list(self) -> pd.DataFrame:
        """Merge the transaction list with the base DataFrame."""
        self.df_base_with_transactions = self.df_base.merge(
            self.transaction_list,
            how="left",
            left_index=True,
            right_index=True,
        )

    def _300_drop_columns(self) -> pd.DataFrame:
        """Drop columns that are not needed."""
        self.df_transaction_clean = self.df_base_with_transactions.drop(
            columns=self.COLS_TO_DROP
        )
