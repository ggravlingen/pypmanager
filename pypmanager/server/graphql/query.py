"""Represent queries."""

from __future__ import annotations

from typing import cast

import pandas as pd
import strawberry

from pypmanager.helpers import get_general_ledger_as_dict
from pypmanager.loader_transaction.const import ColumnNameValues

from .models import LedgerRow


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    def all_general_ledger(self: Query) -> list[LedgerRow]:
        """Return all general ledger rows."""
        output_dict = get_general_ledger_as_dict()

        output_list: list[LedgerRow] = []

        for row in output_dict:
            if pd.isna(row[ColumnNameValues.NO_TRADED]):
                no_traded = None
            else:
                no_traded = cast(float, row[ColumnNameValues.NO_TRADED])

            if pd.isna(row[ColumnNameValues.NO_HELD]):
                no_held = None
            else:
                no_held = cast(float, row[ColumnNameValues.NO_HELD])

            if pd.isna(row[ColumnNameValues.AVG_PRICE]):
                avg_price = None
            else:
                avg_price = cast(float, row[ColumnNameValues.AVG_PRICE])

            if pd.isna(row[ColumnNameValues.AMOUNT]):
                amount = None
            else:
                amount = cast(float, row[ColumnNameValues.AMOUNT])

            if pd.isna(row[ColumnNameValues.COMMISSION]):
                commission = None
            else:
                commission = cast(float, row[ColumnNameValues.COMMISSION])

            output_list.append(
                LedgerRow(
                    report_date=row[ColumnNameValues.TRANSACTION_DATE],
                    broker=row[ColumnNameValues.BROKER],
                    source=row[ColumnNameValues.SOURCE],
                    action=row[ColumnNameValues.TRANSACTION_TYPE_INTERNAL],
                    name=row[ColumnNameValues.NAME],
                    no_traded=no_traded,
                    agg_buy_volume=no_held,
                    average_price=avg_price,
                    amount=amount,
                    commission=commission,
                )
            )

        return output_list
