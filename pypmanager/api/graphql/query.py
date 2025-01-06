"""Represent queries."""

from __future__ import annotations

from datetime import datetime
from typing import cast

import strawberry

from pypmanager.helpers import (
    ResultStatementRow,
    SecurityDataResponse,
    async_pnl_by_year_from_tr,
    async_security_map_isin_to_security,
)
from pypmanager.helpers.chart import ChartData, async_get_market_data_and_transaction
from pypmanager.helpers.market_data import (
    MarketDataOverviewRecord,
    async_get_market_data_overview,
)
from pypmanager.helpers.portfolio import Holding, async_async_get_holdings
from pypmanager.helpers.transaction import TransactionRow, async_get_all_transactions
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    async def current_portfolio(self: Query) -> list[Holding]:
        """Return the current state of the portfolio."""
        return await async_async_get_holdings()

    @strawberry.field
    async def all_transaction(self: Query) -> list[TransactionRow]:
        """Return all transactions."""
        return await async_get_all_transactions()

    @strawberry.field
    async def result_statement(self: Query) -> list[ResultStatementRow]:
        """Return the result statement."""
        async with TransactionRegistry() as registry_obj:
            df_transaction_registry_all = await registry_obj.async_get_registry()
            return await async_pnl_by_year_from_tr(
                df_transaction_registry_all=df_transaction_registry_all
            )

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
    ) -> SecurityDataResponse | None:
        """Return information about a security."""
        all_security = await async_security_map_isin_to_security()
        return cast(SecurityDataResponse | None, all_security.get(isin_code))
