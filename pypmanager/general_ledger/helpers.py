"""Helper functions."""

from datetime import datetime
from typing import Any, cast

import pandas as pd

from pypmanager.ingest.transaction import (
    TransactionRegistry,
)
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues

from .ledger import GeneralLedger


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
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
        ],
        ascending=False,
    )
    output_dict = df_general_ledger.reset_index().to_dict(orient="records")

    return cast(list[dict[str, Any]], output_dict)
