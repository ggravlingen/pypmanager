"""Represent queries."""

from __future__ import annotations

from datetime import datetime
from typing import cast

import numpy as np
import strawberry

from pypmanager.general_ledger import (
    async_get_general_ledger_as_dict,
)
from pypmanager.helpers.chart import ChartData, async_get_market_data_and_transaction
from pypmanager.helpers.market_data import (
    MarketDataOverviewRecord,
    async_get_market_data_overview,
)
from pypmanager.helpers.portfolio import Holdingv2, async_async_get_holdings_v2
from pypmanager.helpers.security import async_load_security_data
from pypmanager.ingest.transaction import (
    ColumnNameValues,
    TransactionRegistry,
    TransactionRegistryColNameValues,
    async_aggregate_income_statement_by_year,
)

from .models import (
    LedgerRow,
    ResultStatementRow,
    SecurityResponse,
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
                broker=row[TransactionRegistryColNameValues.SOURCE_BROKER.value],
                source=row[TransactionRegistryColNameValues.SOURCE_FILE.value],
                action=row[ColumnNameValues.TRANSACTION_TYPE_INTERNAL],
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY],
                no_traded=row[TransactionRegistryColNameValues.SOURCE_VOLUME.value],
                agg_buy_volume=row[ColumnNameValues.NO_HELD],
                amount=row[ColumnNameValues.AMOUNT],
                commission=row[TransactionRegistryColNameValues.SOURCE_FEE],
                cash_flow=row[ColumnNameValues.CASH_FLOW_LOCAL],
                fx=row[TransactionRegistryColNameValues.SOURCE_FX.value],
                average_fx_rate=row[ColumnNameValues.AVG_FX],
                credit=row[ColumnNameValues.CREDIT],
                debit=row[ColumnNameValues.DEBIT],
                account=row[ColumnNameValues.ACCOUNT],
            )
            for row in output_dict
        ]

    @strawberry.field
    async def current_portfolio(self: Query) -> list[Holdingv2]:
        """Return the current state of the portfolio."""
        return await async_async_get_holdings_v2()

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
                commission = row[TransactionRegistryColNameValues.SOURCE_FEE.value]
            else:
                commission = None

            if (
                row[TransactionRegistryColNameValues.SOURCE_ISIN.value] is not None
                or row[TransactionRegistryColNameValues.SOURCE_ISIN.value] != 0
            ):
                isin_code = row[TransactionRegistryColNameValues.SOURCE_ISIN.value]
            else:
                isin_code = None

            output_list.append(
                TransactionRow(
                    transaction_date=index,
                    isin_code=isin_code,
                    broker=row[TransactionRegistryColNameValues.SOURCE_BROKER.value],
                    source=row[TransactionRegistryColNameValues.SOURCE_FILE.value],
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
                    fx=row[TransactionRegistryColNameValues.SOURCE_FX.value],
                    cost_base_average=row[
                        TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                    ],
                    pnl_total=row[
                        TransactionRegistryColNameValues.CALC_PNL_TOTAL.value
                    ],
                    pnl_trade=row[
                        TransactionRegistryColNameValues.CALC_PNL_TRADE.value
                    ],
                    pnl_dividend=row[
                        TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value
                    ],
                    quantity_held=row[
                        TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value
                    ],
                )
            )

        return output_list

    @strawberry.field
    async def result_statement(self: Query) -> list[ResultStatementRow]:
        """Return the result statement."""
        ledger_by_year = await async_aggregate_income_statement_by_year()
        output_list: list[ResultStatementRow] = []

        year_list = [column for column in ledger_by_year.columns if column != "index"]

        for row_index_name, is_total in (
            (TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value, False),
            (TransactionRegistryColNameValues.CALC_PNL_TRADE.value, False),
            (TransactionRegistryColNameValues.CALC_PNL_TOTAL.value, True),
        ):
            filtered_ledger = ledger_by_year[
                ledger_by_year["index"] == row_index_name
            ].reset_index()

            if filtered_ledger.empty:
                continue

            filtered_ledger = filtered_ledger.replace({0: None, np.nan: None})

            values_list = filtered_ledger.loc[0, year_list].tolist()

            output_list.append(
                ResultStatementRow(
                    item_name=row_index_name,
                    year_list=year_list,
                    amount_list=values_list,
                    is_total=is_total,
                )
            )

        return output_list

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
