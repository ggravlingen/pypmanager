"""Represent queries."""

from __future__ import annotations

from typing import cast

import numpy as np
import strawberry

from pypmanager.analytics import async_get_historical_portfolio, async_get_holdings
from pypmanager.general_ledger import get_general_ledger_as_dict
from pypmanager.ingest.transaction import (
    ColumnNameValues,
    load_transaction_files,
)

from .models import (
    HistoricalPortfolioRow,
    LedgerRow,
    PortfolioContentRow,
    TransactionRow,
)


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    async def all_general_ledger(self: Query) -> list[LedgerRow]:
        """Return all general ledger rows."""
        output_dict = get_general_ledger_as_dict()

        return [
            LedgerRow(
                transaction_date=row[ColumnNameValues.TRANSACTION_DATE],
                broker=row[ColumnNameValues.BROKER],
                source=row[ColumnNameValues.SOURCE],
                action=row[ColumnNameValues.TRANSACTION_TYPE_INTERNAL],
                name=row[ColumnNameValues.NAME],
                no_traded=row[ColumnNameValues.NO_TRADED],
                agg_buy_volume=row[ColumnNameValues.NO_HELD],
                average_price=row[ColumnNameValues.AVG_PRICE],
                amount=row[ColumnNameValues.AMOUNT],
                commission=row[ColumnNameValues.COMMISSION],
                cash_flow=row[ColumnNameValues.CASH_FLOW_LOCAL],
                fx=row[ColumnNameValues.FX],
                average_fx_rate=row[ColumnNameValues.AVG_FX],
                credit=row[ColumnNameValues.CREDIT],
                debit=row[ColumnNameValues.DEBIT],
                account=row[ColumnNameValues.ACCOUNT],
            )
            for row in output_dict
        ]

    @strawberry.field
    async def current_portfolio(self: Query) -> list[PortfolioContentRow]:
        """Return the current state of the portfolio."""
        holdings = await async_get_holdings()

        return [
            PortfolioContentRow(
                name=holding.name,
                date_market_value=cast(str, holding.date_market_value),
                invested_amount=holding.invested_amount,
                market_value=holding.market_value,
                current_holdings=holding.current_holdings,
                current_price=holding.current_price,
                average_price=holding.average_price,
                return_pct=holding.return_pct,
                total_pnl=holding.total_pnl,
                realized_pnl=holding.realized_pnl,
                unrealized_pnl=holding.unrealized_pnl,
            )
            for holding in holdings
        ]

    @strawberry.field
    async def historical_portfolio(self: Query) -> list[HistoricalPortfolioRow]:
        """Return historical portfolio data."""
        historical_portfolio = await async_get_historical_portfolio()

        return [
            HistoricalPortfolioRow(
                report_date=row.report_date,
                invested_amount=row.portfolio.invested_amount,
                market_value=row.portfolio.market_value,
                return_pct=row.portfolio.return_pct,
                realized_pnl=row.portfolio.realized_pnl,
                unrealized_pnl=row.portfolio.unrealized_pnl,
            )
            for row in historical_portfolio
        ]

    @strawberry.field
    async def all_transaction(self: Query) -> list[TransactionRow]:
        """Return all transactions."""
        transaction_list = load_transaction_files(sort_by_date_descending=True)
        transaction_list = transaction_list.replace({np.nan: None})

        return [
            TransactionRow(
                transaction_date=index,
                broker=row[ColumnNameValues.BROKER.value],
                source=row[ColumnNameValues.SOURCE.value],
                action=row[ColumnNameValues.TRANSACTION_TYPE.value],
                name=row[ColumnNameValues.NAME.value],
                no_traded=row[ColumnNameValues.NO_TRADED.value],
                price=row[ColumnNameValues.PRICE.value],
                commission=row[ColumnNameValues.COMMISSION.value],
                fx=row[ColumnNameValues.FX.value],
            )
            for index, row in transaction_list.iterrows()
        ]
