"""Represent queries."""

from __future__ import annotations

from typing import cast

import numpy as np
import strawberry

from pypmanager.analytics import async_get_historical_portfolio, async_get_holdings
from pypmanager.general_ledger import (
    async_aggregate_ledger_by_year,
    async_get_general_ledger_as_dict,
)
from pypmanager.ingest.transaction import (
    AccountNameValues,
    ColumnNameValues,
    TransactionRegistry,
    TransactionRegistryColNameValues,
)

from .models import (
    HistoricalPortfolioRow,
    LedgerRow,
    PortfolioContentRow,
    ResultStatementRow,
    TransactionRow,
)


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    async def all_general_ledger(self: Query) -> list[LedgerRow]:
        """Return all general ledger rows."""
        output_dict = await async_get_general_ledger_as_dict()

        return [
            LedgerRow(
                transaction_date=row[
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE
                ],
                broker=row[ColumnNameValues.BROKER],
                source=row[ColumnNameValues.SOURCE],
                action=row[ColumnNameValues.TRANSACTION_TYPE_INTERNAL],
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY],
                no_traded=row[TransactionRegistryColNameValues.SOURCE_VOLUME.value],
                agg_buy_volume=row[ColumnNameValues.NO_HELD],
                average_price=row[ColumnNameValues.AVG_PRICE],
                amount=row[ColumnNameValues.AMOUNT],
                commission=row[TransactionRegistryColNameValues.SOURCE_FEE],
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
        transaction_list = await TransactionRegistry(
            sort_by_date_descending=True
        ).async_get_registry()
        transaction_list = transaction_list.replace({np.nan: None})

        output_list: list[TransactionRow] = []
        for index, row in transaction_list.iterrows():
            if row[TransactionRegistryColNameValues.SOURCE_FEE.value] is not None:
                commission = abs(row[TransactionRegistryColNameValues.SOURCE_FEE.value])
            else:
                commission = None

            output_list.append(
                TransactionRow(
                    transaction_date=index,
                    broker=row[ColumnNameValues.BROKER.value],
                    source=row[ColumnNameValues.SOURCE.value],
                    action=cast(
                        str,
                        row[
                            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value
                        ],
                    ).capitalize(),
                    name=row[
                        TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value
                    ],
                    no_traded=row[TransactionRegistryColNameValues.SOURCE_VOLUME.value],
                    currency=row[
                        TransactionRegistryColNameValues.SOURCE_CURRENCY.value
                    ],
                    price=row[TransactionRegistryColNameValues.SOURCE_PRICE.value],
                    # It makes more sense to use the absolute value of the commission in
                    # this context
                    commission=commission,
                    cash_flow=row[
                        TransactionRegistryColNameValues.CASH_FLOW_NET_FEE_NOMINAL.value
                    ],
                    fx=row[ColumnNameValues.FX.value],
                    cost_base_average=row[
                        TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                    ],
                )
            )

        return output_list

    @strawberry.field
    async def result_statement(self: Query) -> list[ResultStatementRow]:
        """Return the result statement."""
        ledger_by_year = await async_aggregate_ledger_by_year()
        output_list: list[ResultStatementRow] = []

        year_list = [
            column for column in ledger_by_year.columns if column != "ledger_account"
        ]

        for item_name in (
            AccountNameValues.IS_INTEREST.value,
            AccountNameValues.IS_DIVIDEND.value,
            AccountNameValues.IS_PNL.value,
        ):
            filtered_ledger = ledger_by_year[
                ledger_by_year["ledger_account"] == item_name
            ].reset_index()

            if filtered_ledger.empty:
                continue

            filtered_ledger = filtered_ledger.replace({0: None, np.nan: None})

            values_list = filtered_ledger.loc[0, year_list].tolist()

            output_list.append(
                ResultStatementRow(
                    item_name=item_name,
                    year_list=year_list,
                    amount_list=values_list,
                )
            )

        return output_list
