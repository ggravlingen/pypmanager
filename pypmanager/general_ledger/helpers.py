"""Helper functions."""

from datetime import datetime
from typing import Any, cast

import pandas as pd

from pypmanager.ingest.transaction import (
    ColumnNameValues,
    TransactionRegistry,
)

from .ledger import GeneralLedger
from .pandas_algorithm import PandasAlgorithmGeneralLedger


async def async_get_general_ledger(report_date: datetime | None = None) -> pd.DataFrame:
    """Return the general ledger."""
    all_data = await TransactionRegistry(report_date=report_date).async_get_registry()
    return GeneralLedger(transactions=all_data).output_df


async def async_get_general_ledger_as_dict(
    report_date: datetime | None = None,
) -> list[dict[str, Any]]:
    """Get the general ledger converted to dict."""
    df_general_ledger = await async_get_general_ledger(report_date=report_date)
    df_general_ledger = df_general_ledger.sort_values(
        [
            ColumnNameValues.TRANSACTION_DATE,
            ColumnNameValues.NAME,
        ],
        ascending=False,
    )
    output_dict = df_general_ledger.reset_index().to_dict(orient="records")

    return cast(list[dict[str, Any]], output_dict)


async def async_aggregate_ledger_by_year() -> pd.DataFrame:
    """Aggregate the general ledger by year."""
    df_general_ledger = await async_get_general_ledger()

    # Filter all income statement records
    filtered_df = df_general_ledger[
        df_general_ledger[ColumnNameValues.ACCOUNT.value].str.startswith("is_")
    ]

    filtered_df_copy = filtered_df.copy()

    filtered_df_copy["result_value"] = filtered_df_copy.apply(
        PandasAlgorithmGeneralLedger.calculate_result, axis=1
    )

    df_grouped_data = (
        filtered_df_copy.groupby(
            [
                ColumnNameValues.META_TRANSACTION_YEAR.value,
                ColumnNameValues.ACCOUNT.value,
            ]
        )["result_value"]
        .sum()
        .reset_index()
    )

    return df_grouped_data.pivot_table(
        values="result_value",
        index=ColumnNameValues.ACCOUNT.value,
        columns=ColumnNameValues.META_TRANSACTION_YEAR.value,
        fill_value=None,
    ).reset_index()
