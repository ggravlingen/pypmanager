"""Represent queries."""
from __future__ import annotations

import strawberry

from pypmanager.helpers import get_general_ledger_as_dict
from pypmanager.loader_transaction.const import ColumnNameValues

from .models import LedgerRow


@strawberry.type
class Query:
    """GraphQL query."""

    @strawberry.field
    def all_general_ledger(self) -> list[LedgerRow]:
        """Return all general ledger rows."""
        output_dict = get_general_ledger_as_dict()

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
