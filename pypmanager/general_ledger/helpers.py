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
