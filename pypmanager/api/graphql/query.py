"""Represent queries."""

from __future__ import annotations

from datetime import datetime
from typing import cast

import strawberry

from pypmanager.helpers.chart import ChartData, async_get_market_data_and_transaction
from pypmanager.helpers.income_statement import ResultStatementRow, async_pnl_by_year
from pypmanager.helpers.market_data import (
    MarketDataOverviewRecord,
    async_get_market_data_overview,
)
from pypmanager.helpers.portfolio import Holdingv2, async_async_get_holdings_v2
from pypmanager.helpers.security import async_load_security_data
from pypmanager.helpers.transaction import TransactionRow, async_get_all_transactions

from .models import (
    SecurityResponse,
)


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    async def current_portfolio(self: Query) -> list[Holdingv2]:
        """Return the current state of the portfolio."""
        return await async_async_get_holdings_v2()

    @strawberry.field
    async def all_transaction(self: Query) -> list[TransactionRow]:
        """Return all transactions."""
        return await async_get_all_transactions()

    @strawberry.field
    async def result_statement(self: Query) -> list[ResultStatementRow]:
        """Return the result statement."""
        return await async_pnl_by_year()

    @strawberry.field
    async def chart_history(
        self: Query,
        isin_code: str,
        start_date: str,
        end_date: str,
    ) -> list[ChartData]:
        """Return historical prices for a series."""
        calc_start_date = datetime.strptime(  # noqa: DTZ007
            start_date, "%Y-%m-%d"
        ).date()
        calc_end_date = datetime.strptime(  # noqa: DTZ007
            end_date,
            "%Y-%m-%d",
        ).date()

        return await async_get_market_data_and_transaction(
            isin_code=isin_code,
            start_date=calc_start_date,
            end_date=calc_end_date,
        )

    @strawberry.field
    async def market_data_overview(
        self: Query,
    ) -> list[MarketDataOverviewRecord]:
        """Return an overview of available market data."""
        return await async_get_market_data_overview()

    @strawberry.field
    async def security_info(
        self: Query,
        isin_code: str,
    ) -> SecurityResponse | None:
        """Return information about a security."""
        all_security = await async_load_security_data()
        return cast(SecurityResponse | None, all_security.get(isin_code))
