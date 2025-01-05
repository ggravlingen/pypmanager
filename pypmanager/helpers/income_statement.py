"""Helper functions for income statement data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import pandas as pd

from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues


@dataclass
class PnLData:
    """Represent PnL for a security."""

    pnl_total: float | None = None
    pnl_trade: float | None = None
    pnl_dividend: float | None = None
    pnl_unrealized: float | None = None


async def async_pnl_get_isin_map(
    *,
    df_transaction_registry_all: pd.DataFrame,
) -> dict[str, PnLData]:
    """
    Extract PnL data from the transaction registry.

    The function returns a dictionary with isin_code as key and pnl_total as value.
    """
    # Group data and sum pnl_realized and pnl_unrealized by isin_code
    df_pnl = cast(
        pd.DataFrame,
        df_transaction_registry_all.groupby(
            TransactionRegistryColNameValues.SOURCE_ISIN.value
        )
        .agg(
            {
                TransactionRegistryColNameValues.CALC_PNL_TRADE.value: "sum",
                TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value: "sum",
            }
        )
        .reset_index(),
    )

    return {
        row[TransactionRegistryColNameValues.SOURCE_ISIN.value]: PnLData(
            pnl_trade=row[TransactionRegistryColNameValues.CALC_PNL_TRADE.value],
            pnl_dividend=row[TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value],
        )
        for _, row in df_pnl.iterrows()
    }
