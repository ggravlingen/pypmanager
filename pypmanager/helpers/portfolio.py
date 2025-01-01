"""Helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import cast

import pandas as pd
import strawberry

from pypmanager.analytics.holding import Holding
from pypmanager.analytics.portfolio import Portfolio
from pypmanager.general_ledger import async_get_general_ledger
from pypmanager.helpers.market_data import async_get_last_market_data_df
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings
from pypmanager.utils.dt import async_get_last_n_quarters

LOGGER = logging.getLogger(__package__)


async def async_get_holdings(report_date: datetime | None = None) -> list[Holding]:
    """
    Return a list of current holdings.

    Deprecated.
    """
    df_general_ledger = await async_get_general_ledger(report_date=report_date)
    all_securities = cast(
        list[str],
        df_general_ledger[
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY
        ].unique(),
    )

    holdings: list[Holding] = []
    for security_name in all_securities:
        holding = Holding(
            name=security_name,
            df_general_ledger=df_general_ledger,
            report_date=report_date,
        )

        if holding.total_pnl == 0:
            continue

        holdings.append(holding)

    # Order by name
    return sorted(holdings, key=lambda x: x.name)


@dataclass
@strawberry.type
class Holdingv2:
    """Represent a security."""

    name: str
    current_market_value_amount: float

    invested_amount: float | None = None
    date_market_value: date | None = None

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

        if pd.isna(no_units):
            invested_amount = None
        else:
            invested_amount = (
                row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
                * row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value]
            )

        isin_code = row[TransactionRegistryColNameValues.SOURCE_ISIN.value]

        filtered_market_data = df_market_data.query(f"isin_code == '{isin_code}'")

        if filtered_market_data.empty:
            current_market_value_amount = 0.0
            pnl_unrealized = 0.0
            date_market_value = None
        else:
            date_market_value = filtered_market_data.index
            market_price = filtered_market_data.iloc[0]["price"]
            current_market_value_amount = market_price * no_units
            if invested_amount:
                pnl_unrealized = current_market_value_amount - invested_amount
            else:
                pnl_unrealized = 0.0

        output_data.append(
            Holdingv2(
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value],
                invested_amount=invested_amount,
                current_market_value_amount=current_market_value_amount,
                pnl_unrealized=pnl_unrealized,
                date_market_value=date_market_value,
            )
        )

    return sorted(output_data, key=lambda x: x.name)


@dataclass
class PortfolioSnapshot:
    """A point of time snapshot of a portfolio."""

    report_date: date
    portfolio: Portfolio


async def async_get_historical_portfolio() -> list[PortfolioSnapshot]:
    """Return a list of historical portfolios."""
    quarter_list = await async_get_last_n_quarters(no_quarters=8)
    quarter_list.append(datetime.now(Settings.system_time_zone))

    portfolio_data: list[PortfolioSnapshot] = []
    for report_date in quarter_list:
        _report_date = datetime(
            report_date.year,
            report_date.month,
            report_date.day,
            tzinfo=Settings.system_time_zone,
        )
        try:
            holdings = await async_get_holdings(report_date=_report_date)
        except ValueError:
            continue

        portfolio = Portfolio(holdings=holdings)
        portfolio_data.append(
            PortfolioSnapshot(
                report_date=report_date,
                portfolio=portfolio,
            ),
        )

    return portfolio_data
