"""Pandas algorithm for transaction data."""

from __future__ import annotations

from typing import cast

import pandas as pd

from .const import ColumnNameValues, TransactionTypeValues


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

    @staticmethod
    def normalize_fx(row: pd.DataFrame) -> float:
        """Set FX rate to a value."""
        if ColumnNameValues.FX.value not in row:
            return 1.00

        if pd.isna(row[ColumnNameValues.FX.value]):
            return 1.00

        return cast(float, row[ColumnNameValues.FX.value])
