"""Helper functions."""

from datetime import datetime
from typing import Any, cast

import pandas as pd

from pypmanager.ingest.transaction import (
    ColumnNameValues,
    load_transaction_files,
)

from .ledger import GeneralLedger


def get_general_ledger(report_date: datetime | None = None) -> pd.DataFrame:
    """Return the general ledger."""
    all_data = load_transaction_files(report_date=report_date)
    return GeneralLedger(transactions=all_data).output_df


def get_general_ledger_as_dict() -> list[dict[str, Any]]:
    """Get the general ledger converted to dict."""
    df_general_ledger = get_general_ledger()
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
    df_general_ledger = get_general_ledger()

    new_date_column = f"{ColumnNameValues.TRANSACTION_DATE.value}_2"

    # Filter all income statement records
    filtered_df = df_general_ledger[
        df_general_ledger[ColumnNameValues.ACCOUNT.value].str.startswith("is_")
    ]

    filtered_df_copy = filtered_df.copy()

    filtered_df_copy[new_date_column] = pd.to_datetime(filtered_df_copy.index)

    filtered_df_copy["year"] = filtered_df_copy[new_date_column].dt.year

    filtered_df_copy["net"] = (
        filtered_df_copy[ColumnNameValues.CREDIT]
        - filtered_df_copy[ColumnNameValues.DEBIT]
    )

    return (
        filtered_df_copy.groupby(["year", ColumnNameValues.ACCOUNT.value])["net"]
        .sum()
        .reset_index()
    )
