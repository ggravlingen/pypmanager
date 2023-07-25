"""Represent queries."""
from __future__ import annotations

import strawberry

from pypmanager.helpers import get_general_ledger
from pypmanager.loader_transaction.const import ColumnNameValues

from .models import LedgerRow


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    def all_general_ledger(self) -> list[LedgerRow]:
        """Return all general ledger rows."""
        df_general_ledger = get_general_ledger()
        df_general_ledger = df_general_ledger.sort_values(
            [
                ColumnNameValues.TRANSACTION_DATE,
                ColumnNameValues.NAME,
            ],
            ascending=False,
        )
        output_dict = df_general_ledger.reset_index().to_dict(orient="records")

        output_data: list[LedgerRow] = []

        for row in output_dict:
            output_data.append(
                LedgerRow(
                    date=row[ColumnNameValues.TRANSACTION_DATE],
                    broker=row[ColumnNameValues.BROKER],
                    source=row[ColumnNameValues.SOURCE],
                )
            )

        return output_data
