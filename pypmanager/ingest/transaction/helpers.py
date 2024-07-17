"""Helper functions."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pandas as pd

from pypmanager.ingest.transaction.base_loader import (
    FILTER_STATEMENT,
    REPLACE_CONFIG,
    _cleanup_number,
    _normalize_amount,
    _normalize_fx,
    _normalize_no_traded,
)
from pypmanager.ingest.transaction.const import (
    DTYPES_MAP,
    NUMBER_COLS,
    ColumnNameValues,
)

from .avanza import AvanzaLoader
from .generic import GenericLoader
from .lysa import LysaLoader

if TYPE_CHECKING:
    from datetime import datetime


class TransactionRegistry:
    """
    Create a normalised registry for all transactions.

    This registry is the basis for all other calculations.
    """

    def __init__(
        self: TransactionRegistry,
        report_date: datetime | None = None,
        *,
        sort_by_date_descending: bool = False,
    ) -> None:
        """Init class."""
        self.report_date = report_date
        self.sort_by_date_descending = sort_by_date_descending

        self.df_all_transactions = self._load_transaction_files()

        self._set_index()
        self._normalize_transaction_type()
        self._filter_transactions()
        self._cleanup_df()
        self._convert_data_types()
        self._normalize_data()

        if sort_by_date_descending:
            self.df_all_transactions.sort_index(ascending=False)

    def _load_transaction_files(self: TransactionRegistry) -> pd.DataFrame:
        """Load transaction files and return a sorted DataFrame."""
        df_generic = GenericLoader(self.report_date).df_final
        df_avanza = AvanzaLoader(self.report_date).df_final
        df_lysa = LysaLoader(self.report_date).df_final

        return pd.concat([df_generic, df_avanza, df_lysa])

    def _set_index(self: TransactionRegistry) -> None:
        """Set index."""
        df_raw = self.df_all_transactions.copy()

        if ColumnNameValues.TRANSACTION_DATE.value in df_raw.columns:
            df_raw = df_raw.set_index(ColumnNameValues.TRANSACTION_DATE.value)

        self.df_all_transactions = df_raw

    def _normalize_transaction_type(self: TransactionRegistry) -> None:
        """
        Normalize transaction types.

        In the source data, transactions will be named differently. To enable
        calculations, we replace the names in the source data with our internal names.
        """
        df_raw = self.df_all_transactions.copy()

        for config in REPLACE_CONFIG:
            for event in config.search:
                df_raw[ColumnNameValues.TRANSACTION_TYPE] = df_raw[
                    ColumnNameValues.TRANSACTION_TYPE
                ].replace(event, config.target)
        self.df_all_transactions = df_raw

    def _filter_transactions(self: TransactionRegistry) -> None:
        """Remove transactions we are not able to process."""
        df_raw = self.df_all_transactions.copy()
        df_raw = df_raw.query(
            f"{ColumnNameValues.TRANSACTION_TYPE} in {FILTER_STATEMENT}",
        )
        self.df_all_transactions = df_raw

    def _cleanup_df(self: TransactionRegistry) -> None:
        """Cleanup dataframe."""
        df_raw = self.df_all_transactions.copy()

        # Ensure all number columns are floats
        for col in NUMBER_COLS:
            if col in df_raw.columns:
                df_raw[col] = df_raw.apply(
                    lambda x, _col=col: _cleanup_number(x[_col]),
                    axis=1,
                )

        # Replace dashes with 0
        for col in (
            ColumnNameValues.COMMISSION,
            ColumnNameValues.ISIN_CODE,
        ):
            if col in df_raw.columns:
                with contextlib.suppress(AttributeError):
                    df_raw[col] = df_raw[col].str.replace("-", "").replace("", 0)

        self.df_all_transactions = df_raw

    def _convert_data_types(self: TransactionRegistry) -> None:
        """Convert columns to correct data types."""
        df_raw = self.df_all_transactions.copy()

        for key, val in DTYPES_MAP.items():
            if key in df_raw.columns:
                try:
                    df_raw[key] = df_raw[key].astype(val)
                except ValueError as err:
                    msg = f"Unable to parse {key}"
                    raise ValueError(msg) from err

        self.df_all_transactions = df_raw

    def _normalize_data(self: TransactionRegistry) -> None:
        """Make sure data is calculated in the same way."""
        df_raw = self.df_all_transactions.copy()

        df_raw[ColumnNameValues.NO_TRADED] = df_raw.apply(_normalize_no_traded, axis=1)
        df_raw[ColumnNameValues.AMOUNT] = df_raw.apply(_normalize_amount, axis=1)
        df_raw[ColumnNameValues.FX] = df_raw.apply(_normalize_fx, axis=1)

        self.df_all_transactions = df_raw

    async def async_get_registry(self) -> pd.DataFrame:
        """Get registry."""
        return self.df_all_transactions
