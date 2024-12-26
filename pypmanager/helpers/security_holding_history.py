"""Build a dataframe what contains historical metrics for a held security."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, cast

import numpy as np
import pandas as pd

from pypmanager.ingest.transaction.const import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
)
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class ColumnAppendConfig:
    """Configuration to append columns."""

    column: str
    callable: Callable[[pd.DataFrame], pd.DataFrame]


class SecurityHoldingHistoryPandasAlgorithm:
    """Pandas algorithms for SecurityHoldingHistory class."""

    @staticmethod
    def clean_calc_agg_sum_quantity_held(row: pd.Series) -> float | None:
        """Test."""
        if row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value] > 0:
            return cast(
                float,
                row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value],
            )

        # Everything has been sold, just return 0
        if (
            row[
                TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value
            ]
            is True
        ):
            return 0.0

        return None


# These columns are appended to the transaction registry
COLUMN_APPEND: tuple[ColumnAppendConfig, ...] = (
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.PRICE_PER_UNIT.value,
        callable=SecurityHoldingHistoryPandasAlgorithm.clean_calc_agg_sum_quantity_held,
    ),
)


class SecurityHoldingHistory:
    """
    Build a dataframe what contains historical metrics for a held security.

    The end result is available in the method async_get_data().
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

    COLS_TO_DROP_LEVEL_2: ClassVar = [
        TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD,
        TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value,
    ]

    df_base: pd.DataFrame
    df_base_with_transactions: pd.DataFrame
    df_transaction_clean: pd.DataFrame
    df_transaction_filled: pd.DataFrame

    def __init__(
        self,
        *,
        isin_code: str,
        df_transaction_registry: pd.DataFrame,
    ) -> None:
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
        self._400_fix_missing_values()

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

    def _400_fix_missing_values(self) -> pd.DataFrame:
        """Fix missing values."""
        df_raw = self.df_transaction_clean.copy()

        for config in COLUMN_APPEND:
            df_raw[config.column] = df_raw.apply(config.callable, axis=1)

        # Fill missing values
        df_raw[TransactionRegistryColNameValues.PRICE_PER_UNIT.value] = df_raw[
            TransactionRegistryColNameValues.PRICE_PER_UNIT.value
        ].ffill()

        df_raw = df_raw.drop(columns=self.COLS_TO_DROP_LEVEL_2)

        # Fill NaN values with None
        df_raw = df_raw.replace({np.nan: None})

        self.df_transaction_filled = df_raw

    async def async_get_data(self) -> pd.DataFrame:
        """Return the DataFrame."""
        return self.df_transaction_filled
