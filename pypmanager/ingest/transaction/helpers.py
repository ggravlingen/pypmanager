"""Helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
)

from .transaction_registry import TransactionRegistry

if TYPE_CHECKING:
    from datetime import datetime

    import pandas as pd


async def async_aggregate_income_statement_by_year(
    report_date: datetime | None = None,
) -> pd.DataFrame:
    """Aggregate the general ledger by year."""
    df_transaction_registry = await TransactionRegistry(
        report_date=report_date
    ).async_get_registry()

    filtered_df_copy = df_transaction_registry.copy()

    df_grouped_data = (
        filtered_df_copy.groupby(
            [
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR.value,
            ]
        )[
            [
                TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value,
                TransactionRegistryColNameValues.CALC_PNL_TRADE.value,
                TransactionRegistryColNameValues.CALC_PNL_TOTAL.value,
            ]
        ]
        .sum()
        .reset_index()
    )

    return df_grouped_data.pivot_table(
        values=[
            TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value,
            TransactionRegistryColNameValues.CALC_PNL_TRADE.value,
            TransactionRegistryColNameValues.CALC_PNL_TOTAL.value,
        ],
        columns=TransactionRegistryColNameValues.META_TRANSACTION_YEAR.value,
        fill_value=None,
    ).reset_index()
