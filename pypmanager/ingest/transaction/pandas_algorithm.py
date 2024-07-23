"""Pandas algorithm for transaction data."""

from __future__ import annotations

from typing import cast

import pandas as pd

from .const import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)


class PandasAlgorithm:
    """Pandas algorithm for transaction data."""

    @staticmethod
    def calculate_cash_flow_net_fee_nominal(row: pd.DataFrame) -> float:
        """Calculate nominal total cash flow, including fees, for a transaction."""
        if (turnover := cast(float | None, row[ColumnNameValues.AMOUNT.value])) is None:
            return 0.0

        if row[ColumnNameValues.COMMISSION.value] is None:
            commission = 0.0
        else:
            commission = cast(float, row[ColumnNameValues.COMMISSION.value])

        return turnover + commission

    @staticmethod
    def calculate_cash_flow_gross_fee_nominal(row: pd.DataFrame) -> float:
        """Calculate nominal total cash flow, excluding fees, for a transaction."""
        if (turnover := cast(float | None, row[ColumnNameValues.AMOUNT.value])) is None:
            return 0.0

        return turnover

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

    @staticmethod
    def calculate_adjusted_price_per_unit(group: pd.DataFrame) -> pd.DataFrame:
        """Calculate adjusted price per unit."""
        group[TransactionRegistryColNameValues.INTERNAL_TURNOVER.value] = group.apply(
            lambda x: (
                (
                    x[ColumnNameValues.TRANSACTION_TYPE.value]
                    == TransactionTypeValues.BUY.value
                )
                - (
                    x[ColumnNameValues.TRANSACTION_TYPE.value]
                    == TransactionTypeValues.SELL.value
                )
            )
            * x[ColumnNameValues.AMOUNT.value],
            axis=1,
        )

        group[TransactionRegistryColNameValues.PRICE_PER_UNIT.value] = 0.0
        last_entry_price = 0.0

        current_turnover = 0.0
        for index, row in group.iterrows():
            current_turnover += row[
                TransactionRegistryColNameValues.INTERNAL_TURNOVER.value
            ]

            if (
                row[ColumnNameValues.TRANSACTION_TYPE.value]
                == TransactionTypeValues.BUY.value
            ):
                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ] = (
                    current_turnover
                    / row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
                )

            if (
                row[ColumnNameValues.TRANSACTION_TYPE.value]
                == TransactionTypeValues.SELL.value
            ):
                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ] = last_entry_price

            # There might be fractional rounding errors when closing a position so we
            # guard against that here
            if (
                round(
                    row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value],
                    0,
                )
                == 0
            ):
                current_turnover = 0.0
                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ] = None
                group.at[  # noqa: PD008
                    index,
                    TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value,
                ] = None
                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.INTERNAL_TURNOVER.value
                ] = None

            last_entry_price = group.at[  # noqa: PD008
                index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
            ]

        return group
