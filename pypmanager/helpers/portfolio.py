"""Helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
import logging

import pandas as pd
import strawberry

from pypmanager.helpers.market_data import async_get_last_market_data_df
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry

LOGGER = logging.getLogger(__package__)


@dataclass
@strawberry.type
class Holdingv2:
    """Represent a security."""

    isin_code: str
    name: str
    current_market_value_amount: float

    quantity_held: float | None = None
    cost_base_average: float | None = None

    invested_amount: float | None = None
    market_value_date: date | None = None
    market_value_price: float | None = None

    pnl_total: float | None = None
    pnl_realized: float | None = None
    pnl_unrealized: float | None = None


async def async_async_get_holdings_v2() -> list[Holdingv2]:
    """Get a list of current holdings, including current market value."""
    output_data: list[Holdingv2] = []
    transaction_registry = await TransactionRegistry().async_get_current_holding()

    df_market_data = await async_get_last_market_data_df()

    for _, row in transaction_registry.iterrows():
        no_units = row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
        average_cost = row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value]

        if pd.isna(no_units):
            no_units = None

        if pd.isna(average_cost):
            average_cost = None

        if not no_units or not average_cost:
            invested_amount = None
        else:
            invested_amount = no_units * average_cost

        isin_code = row[TransactionRegistryColNameValues.SOURCE_ISIN.value]

        filtered_market_data = df_market_data.query(f"isin_code == '{isin_code}'")

        if filtered_market_data.empty:
            current_market_value_amount = 0.0
            pnl_unrealized = 0.0
            market_value_date = None
            market_value_price = None
        else:
            market_value_date = filtered_market_data.index[0].date()
            market_value_price = filtered_market_data.iloc[0]["price"]

            if no_units:
                current_market_value_amount = market_value_price * no_units
            else:
                current_market_value_amount = 0.0

            if pd.isna(current_market_value_amount):
                current_market_value_amount = 0.0
                pnl_unrealized = 0.0

            if invested_amount:
                pnl_unrealized = current_market_value_amount - invested_amount
            else:
                pnl_unrealized = None

        output_data.append(
            Holdingv2(
                isin_code=isin_code,
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value],
                quantity_held=no_units,
                cost_base_average=average_cost,
                invested_amount=invested_amount,
                current_market_value_amount=current_market_value_amount,
                pnl_unrealized=pnl_unrealized,
                market_value_date=market_value_date,
                market_value_price=market_value_price,
            )
        )

    return sorted(output_data, key=lambda x: x.name)
