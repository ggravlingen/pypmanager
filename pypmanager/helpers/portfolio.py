"""Helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
import logging

import pandas as pd
import strawberry

from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry

from .income_statement import PnLData, async_pnl_map_isin_to_pnl_data
from .market_data import async_get_last_market_data_df

LOGGER = logging.getLogger(__package__)


@dataclass
@strawberry.type
class Holding:
    """Represent a security."""

    isin_code: str
    name: str
    current_market_value_amount: float | None = None

    quantity_held: float | None = None
    cost_base_average: float | None = None

    invested_amount: float | None = None
    market_value_date: date | None = None
    market_value_price: float | None = None

    pnl_total: float | None = None
    pnl_trade: float | None = None
    pnl_dividend: float | None = None
    pnl_unrealized: float | None = None


async def async_get_holdings_base() -> tuple[
    pd.DataFrame, pd.DataFrame, dict[str, PnLData], pd.DataFrame
]:
    """Get base data needed for holdings calculations.

    Returns:
        Tuple containing:
        - Full portfolio dataframe
        - All transactions dataframe
        - PnL data mapping
        - Market data dataframe
    """
    # Fetch transaction data
    async with TransactionRegistry() as registry_obj:
        df_transaction_registry_full_portfolio = (
            await registry_obj.async_get_full_portfolio()
        )
        df_transaction_registry_all = await registry_obj.async_get_registry()

        # Calculate PnL data
        pnl_map_isin_to_pnl_data = await async_pnl_map_isin_to_pnl_data(
            df_transaction_registry_all=df_transaction_registry_all
        )

        # Get market data
        df_market_data = await async_get_last_market_data_df()

        return (
            df_transaction_registry_full_portfolio,
            df_transaction_registry_all,
            pnl_map_isin_to_pnl_data,
            df_market_data,
        )


async def async_get_holdings() -> list[Holding]:
    """Get a list of current holdings, including current market value."""
    output_data: list[Holding] = []

    (
        df_transaction_registry_full_portfolio,
        _,
        pnl_map_isin_to_pnl_data,
        df_market_data,
    ) = await async_get_holdings_base()

    for _, row in df_transaction_registry_full_portfolio.iterrows():
        # We only want to include securities with an ISIN code
        if (isin_code := row[TransactionRegistryColNameValues.SOURCE_ISIN.value]) in [
            "nan",
            "0",
        ]:
            continue

        filtered_market_data = df_market_data.query(f"isin_code == '{isin_code}'")

        no_units = row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
        average_cost = row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value]

        no_units = None if pd.isna(no_units) else no_units
        average_cost = None if pd.isna(average_cost) else average_cost

        invested_amount = (
            None if not no_units or not average_cost else no_units * average_cost
        )

        if filtered_market_data.empty:
            current_market_value_amount = pnl_unrealized = market_value_date = (
                market_value_price
            ) = None
        else:
            market_value_date = filtered_market_data.index[0].date()
            market_value_price = filtered_market_data.iloc[0]["price"]
            current_market_value_amount = (
                market_value_price * no_units if no_units else None
            )
            pnl_unrealized = (
                None
                if pd.isna(current_market_value_amount) or invested_amount is None
                else current_market_value_amount - invested_amount
            )
        pnl_data = pnl_map_isin_to_pnl_data.get(isin_code, None)

        output_data.append(
            Holding(
                isin_code=isin_code,
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value],
                quantity_held=no_units,
                cost_base_average=average_cost,
                invested_amount=invested_amount,
                current_market_value_amount=current_market_value_amount,
                pnl_total=pnl_data.pnl_total if pnl_data else None,
                pnl_trade=pnl_data.pnl_trade if pnl_data else None,
                pnl_dividend=pnl_data.pnl_dividend if pnl_data else None,
                pnl_unrealized=pnl_unrealized,
                market_value_date=market_value_date,
                market_value_price=market_value_price,
            )
        )

    return sorted(output_data, key=lambda x: x.name)


async def async_get_holding_by_isin(isin_code: str) -> Holding | None:
    """Get a single holding by ISIN code.

    Args:
        isin_code: The ISIN code to retrieve

    Returns:
        A Holding object if found, None otherwise
    """
    (
        df_transaction_registry_full_portfolio,
        _,
        pnl_map_isin_to_pnl_data,
        df_market_data,
    ) = await async_get_holdings_base()

    # Filter the portfolio to only the requested ISIN
    filtered_portfolio = df_transaction_registry_full_portfolio[
        df_transaction_registry_full_portfolio[
            TransactionRegistryColNameValues.SOURCE_ISIN.value
        ]
        == isin_code
    ]

    if filtered_portfolio.empty:
        return None

    row = filtered_portfolio.iloc[0]

    filtered_market_data = df_market_data.query(f"isin_code == '{isin_code}'")

    no_units = row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
    average_cost = row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value]

    no_units = None if pd.isna(no_units) else no_units
    average_cost = None if pd.isna(average_cost) else average_cost

    invested_amount = (
        None if not no_units or not average_cost else no_units * average_cost
    )

    if filtered_market_data.empty:
        current_market_value_amount = pnl_unrealized = market_value_date = (
            market_value_price
        ) = None
    else:
        market_value_date = filtered_market_data.index[0].date()
        market_value_price = filtered_market_data.iloc[0]["price"]
        current_market_value_amount = (
            market_value_price * no_units if no_units else None
        )
        pnl_unrealized = (
            None
            if pd.isna(current_market_value_amount) or invested_amount is None
            else current_market_value_amount - invested_amount
        )

    pnl_data = pnl_map_isin_to_pnl_data.get(isin_code, None)

    return Holding(
        isin_code=isin_code,
        name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value],
        quantity_held=no_units,
        cost_base_average=average_cost,
        invested_amount=invested_amount,
        current_market_value_amount=current_market_value_amount,
        pnl_total=pnl_data.pnl_total if pnl_data else None,
        pnl_trade=pnl_data.pnl_trade if pnl_data else None,
        pnl_dividend=pnl_data.pnl_dividend if pnl_data else None,
        pnl_unrealized=pnl_unrealized,
        market_value_date=market_value_date,
        market_value_price=market_value_price,
    )
