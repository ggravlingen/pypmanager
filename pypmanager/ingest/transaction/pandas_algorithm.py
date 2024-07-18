"""Pandas algorithm for transaction data."""

from __future__ import annotations

from typing import cast

import pandas as pd

from .const import ColumnNameValues, TransactionTypeValues


class PandasAlgorithm:
    """Pandas algorithm for transaction data."""

    @staticmethod
    def calculate_cash_flow_nominal(row: pd.DataFrame) -> float:
        """Calculate nominal total cash flow for a transaction."""
        if (amount := cast(float | None, row[ColumnNameValues.AMOUNT.value])) is None:
            return 0.0

        if row[ColumnNameValues.COMMISSION.value] is None:
            commission = 0.0
        else:
            commission = cast(float, row[ColumnNameValues.COMMISSION.value])

        return amount + commission

    @staticmethod
    def cleanup_number(value: str | None) -> float | None:
        """Make sure values are converted to floats."""
        if value is None:
            return None

        if (value := f"{value}") == "-":
            return 0

        value = value.replace(",", ".")
        value = value.replace(" ", "")

        try:
            return float(value)
        except ValueError as err:
            msg = f"Unable to parse {value}"
            raise ValueError(msg) from err

    @staticmethod
    def normalize_amount(row: pd.DataFrame) -> float:
        """Calculate amount if nan."""
        if row[ColumnNameValues.TRANSACTION_TYPE.value] in [
            TransactionTypeValues.CASHBACK.value,
            TransactionTypeValues.FEE.value,
        ]:
            amount = row[ColumnNameValues.AMOUNT.value]
        else:
            amount = (
                row[ColumnNameValues.NO_TRADED.value]
                * row[ColumnNameValues.PRICE.value]
            )

        # Buy and tax is a negative cash flow for us
        if row[ColumnNameValues.TRANSACTION_TYPE.value] in [
            TransactionTypeValues.BUY.value,
            TransactionTypeValues.TAX.value,
            TransactionTypeValues.FEE.value,
        ]:
            amount = abs(amount) * -1
        else:
            amount = abs(amount)

        return cast(float, amount)

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
        """Return FX rate or default to 1.00."""
        if ColumnNameValues.FX.value not in row or pd.isna(
            row[ColumnNameValues.FX.value]
        ):
            return 1.00

        return cast(float, row[ColumnNameValues.FX.value])
