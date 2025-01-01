"""Helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import cast

from pypmanager.analytics.holding import Holding
from pypmanager.analytics.portfolio import Portfolio
from pypmanager.general_ledger import async_get_general_ledger
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings
from pypmanager.utils.dt import async_get_last_n_quarters

LOGGER = logging.getLogger(__package__)


async def async_get_holdings(report_date: datetime | None = None) -> list[Holding]:
    """Return a list of current holdings."""
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
class Holdingv2:
    """Represent a security."""

    name: str
    current_holding: float
    current_market_value: float


async def async_async_get_holdings_v2() -> list[Holdingv2]:
    """Get a list of current holdings, including current market value."""
    output_data: list[Holdingv2] = []
    transaction_registry = await TransactionRegistry().async_get_current_holding()
    for _, row in transaction_registry.iterrows():
        output_data.append(
            Holdingv2(
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value],
                current_holding=row[
                    TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value
                ],
                current_market_value=0.0,
            )
        )

    return output_data


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
