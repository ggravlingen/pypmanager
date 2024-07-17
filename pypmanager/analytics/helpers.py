"""Helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import cast

from pypmanager.general_ledger import async_get_general_ledger
from pypmanager.ingest.transaction import ColumnNameValues
from pypmanager.settings import Settings
from pypmanager.utils.dt import async_get_last_n_quarters

from .holding import Holding
from .portfolio import Portfolio

LOGGER = logging.getLogger(__package__)


async def async_get_holdings(report_date: datetime | None = None) -> list[Holding]:
    """Return a list of current holdings."""
    df_general_ledger = await async_get_general_ledger(report_date=report_date)
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
        holdings = await async_get_holdings(report_date=_report_date)
        portfolio = Portfolio(holdings=holdings)
        portfolio_data.append(
            PortfolioSnapshot(
                report_date=report_date,
                portfolio=portfolio,
            ),
        )

    return portfolio_data
