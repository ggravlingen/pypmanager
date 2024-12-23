"""The general ledger."""

from __future__ import annotations

from typing import Any
import warnings

import numpy as np
import pandas as pd

from pypmanager.ingest.transaction import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
)
from pypmanager.settings import Settings

from .calculate_aggregates import CalculateAggregates
from .transaction_macro import _amend_row


def calculate_results(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the general ledger."""
    all_securities_name = data[
        TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value
    ].unique()

    dfs: list[pd.DataFrame] = []

    for security_name in all_securities_name:
        if Settings.debug_name and Settings.debug_name not in security_name:
            continue

        df_data = data.query(
            f"{TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value} == "
            f"'{security_name}'"
        )
        df_result = CalculateAggregates(df_data).output_data

        dfs.append(df_result)

    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)

        return pd.concat(dfs, ignore_index=False)


class GeneralLedger:
    """General ledger."""

    ledger_list: list[dict[str, Any]]
    ledger_df: pd.DataFrame
    output_df: pd.DataFrame

    def __init__(self: GeneralLedger, transactions: pd.DataFrame) -> None:
        """Init."""
        self.transactions = calculate_results(transactions)

        self._transactions_to_dict()
        self._create_ledger()
        self._set_date_index()

    def _transactions_to_dict(self: GeneralLedger) -> None:
        """Convert transactions to dict."""
        self.ledger_list = self.transactions.reset_index().to_dict(orient="records")

    def _create_ledger(self: GeneralLedger) -> None:
        """Create ledger."""
        ledger_list: list[dict[str, Any]] = []
        for row in self.ledger_list:
            ledger_list.extend(_amend_row(row=row))

        self.output_df = pd.DataFrame(ledger_list)

    def _set_date_index(self: GeneralLedger) -> None:
        """Set index to date."""
        df_tmp = self.output_df.copy()
        # Convert index to a date of format YYYY-MM-DD
        df_tmp[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE] = (
            df_tmp[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE]
            .astype(str)
            .str[:10]
        )
        df_tmp[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE] = (
            pd.to_datetime(
                df_tmp[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE],
                format="%Y-%m-%d",
            )
        )
        df_tmp = df_tmp.set_index(
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
        )
        df_tmp.index = df_tmp.index

        # Sort by transaction date
        df_tmp = df_tmp.rename_axis(
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
        ).sort_values(
            by=[
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
                ColumnNameValues.TRANSACTION_TYPE_INTERNAL,
            ],
            ascending=[True, True],
        )

        # Make sure the dataframe does not contain None
        df_tmp = df_tmp.replace({np.nan: None})

        self.output_df = df_tmp

    def __repr__(self: GeneralLedger) -> str:
        """Repr."""
        return f"GeneralLedger of ({len(self.output_df)}) records"

    def __str__(self: GeneralLedger) -> str:
        """Str."""
        return f"GeneralLedger of ({len(self.output_df)}) records"

    async def async_get_volume_by_date(self: GeneralLedger) -> pd.DataFrame:
        """Get volume by date."""
        return (
            self.output_df.groupby(
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value
            )[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
            .sum()
            .reset_index()
        )
