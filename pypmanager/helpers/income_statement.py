"""Helper functions for income statement data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TC003
from typing import cast

import numpy as np
import pandas as pd
import strawberry

from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry


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


@strawberry.type
@dataclass
class ResultStatementRow:
    """Represent a row in the result statement."""

    item_name: str
    year_list: list[int]
    amount_list: list[float | None]
    is_total: bool


async def async_pnl_by_year(
    report_date: datetime | None = None,
) -> list[ResultStatementRow]:
    """Aggregate the transaction registry by year."""
    output_list: list[ResultStatementRow] = []

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

    df_ledger_by_year = df_grouped_data.pivot_table(
        values=[
            TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value,
            TransactionRegistryColNameValues.CALC_PNL_TRADE.value,
            TransactionRegistryColNameValues.CALC_PNL_TOTAL.value,
        ],
        columns=TransactionRegistryColNameValues.META_TRANSACTION_YEAR.value,
        fill_value=None,
    ).reset_index()

    year_list = [column for column in df_ledger_by_year.columns if column != "index"]

    for row_index_name, is_total in (
        (TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value, False),
        (TransactionRegistryColNameValues.CALC_PNL_TRADE.value, False),
        (TransactionRegistryColNameValues.CALC_PNL_TOTAL.value, True),
    ):
        filtered_ledger = df_ledger_by_year[
            df_ledger_by_year["index"] == row_index_name
        ].reset_index()

        filtered_ledger = filtered_ledger.replace({0: None, np.nan: None})

        values_list = filtered_ledger.loc[0, year_list].tolist()

        output_list.append(
            ResultStatementRow(
                item_name=row_index_name,
                year_list=year_list,
                amount_list=values_list,
                is_total=is_total,
            )
        )

    return output_list
