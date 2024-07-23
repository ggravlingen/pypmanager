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
    all_securities_name = data.name.unique()

    dfs: list[pd.DataFrame] = []

    for name in all_securities_name:
        if Settings.debug_name and Settings.debug_name not in name:
            continue

        df_data = data.query(f"name == '{name}'")
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

        self.transactions_to_dict()
        self.create_ledger()
        self.set_date_index()

    def transactions_to_dict(self: GeneralLedger) -> None:
        """Convert transactions to dict."""
        self.ledger_list = self.transactions.reset_index().to_dict(orient="records")

    def create_ledger(self: GeneralLedger) -> None:
        """Create ledger."""
        ledger_list: list[dict[str, Any]] = []
        for row in self.ledger_list:
            ledger_list.extend(_amend_row(row=row))

        self.output_df = pd.DataFrame(ledger_list)

    def set_date_index(self: GeneralLedger) -> None:
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
