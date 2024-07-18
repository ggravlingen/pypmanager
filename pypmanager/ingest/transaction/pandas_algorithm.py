"""Pandas algorithm for transaction data."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .const import ColumnNameValues, TransactionTypeValues

if TYPE_CHECKING:
    import pandas as pd


class PandasAlgorithm:
    """Pandas algorithm for transaction data."""

    @staticmethod
    def normalize_no_traded(row: pd.DataFrame) -> float:
        """Calculate number of units traded."""
        no_traded = cast(float, row[ColumnNameValues.NO_TRADED.value])

        if row[ColumnNameValues.TRANSACTION_TYPE.value] in [
            TransactionTypeValues.BUY.value,
            TransactionTypeValues.DIVIDEND.value,
        ]:
            return no_traded

        return abs(no_traded) * -1
