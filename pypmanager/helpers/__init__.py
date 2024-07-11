"""Helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
import logging
from typing import cast

from pypmanager.analytics.holding import Holding
from pypmanager.analytics.portfolio import Portfolio
from pypmanager.general_ledger import get_general_ledger
from pypmanager.loader_transaction.const import ColumnNameValues
from pypmanager.utils.dt import async_get_last_n_quarters

LOGGER = logging.getLogger(__package__)


async def get_holdings(report_date: date | None = None) -> list[Holding]:
    """Return a list of current holdings."""
    df_general_ledger = get_general_ledger()
    all_securities = cast(list[str], df_general_ledger[ColumnNameValues.NAME].unique())

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
class PortfolioSnapshot:
    """A point of time snapshot of a portfolio."""

    report_date: date
    portfolio: Portfolio


async def get_historical_portfolio() -> list[PortfolioSnapshot]:
    """Return a list of historical portfolios."""
    quarter_list = await async_get_last_n_quarters(no_quarters=8)
    quarter_list.append(datetime.now(UTC).date())

    portfolio_data: list[PortfolioSnapshot] = []
    for report_date in quarter_list:
        holdings = await get_holdings(report_date=report_date)
        portfolio = Portfolio(holdings=holdings)
        portfolio_data.append(
            PortfolioSnapshot(
                report_date=report_date,
                portfolio=portfolio,
            ),
        )

    return portfolio_data
