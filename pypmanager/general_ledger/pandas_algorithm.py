"""Pandas algorithm for the general ledger data."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pypmanager.ingest.transaction.const import ColumnNameValues

if TYPE_CHECKING:
    import pandas as pd


class PandasAlgorithmGeneralLedger:
    """Pandas algorithm for the general ledger."""

    @staticmethod
    def calculate_result(row: pd.DataFrame) -> float:
        """Calculate the result."""
        if row[ColumnNameValues.CREDIT.value] is not None:
            return cast(float, row[ColumnNameValues.CREDIT.value])

        if row[ColumnNameValues.DEBIT.value] is not None:
            return -cast(float, row[ColumnNameValues.DEBIT.value])

        return 0.0
