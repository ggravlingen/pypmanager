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
    def turnover_or_other_cash_flow(row: pd.DataFrame) -> float | None:
        """
        Return turnover or other cash flow.

        The returned value has correct sign.
        """
        if (
            row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
            in [
                # This should be expanded
                TransactionTypeValues.DIVIDEND.value,
                TransactionTypeValues.DEPOSIT.value,
            ]
            and TransactionRegistryColNameValues.SOURCE_OTHER_CASH_FLOW.value in row
        ):
            return cast(
                "float",
                row[TransactionRegistryColNameValues.SOURCE_OTHER_CASH_FLOW.value],
            )

        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] not in (
            TransactionTypeValues.BUY.value,
            TransactionTypeValues.SELL.value,
        ):
            return None

        price = cast("float", row[TransactionRegistryColNameValues.SOURCE_PRICE.value])

        # Return turnover for buy transactions (negative cash flow for us)
        if (
            row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
            == TransactionTypeValues.BUY.value
        ):
            return (
                cast(
                    "float",
                    abs(row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]),
                )
                * -1.0
                * price
            )

        # Sell
        return (
            cast(
                "float",
                abs(row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]),
            )
            * price
        )

    @staticmethod
    def calculate_cash_flow_net_fee_nominal(row: pd.DataFrame) -> float:
        """Calculate nominal total cash flow, including fees, for a transaction."""
        if (
            turnover_or_other_cf := cast(
                "float | None",
                row[TransactionRegistryColNameValues.CALC_TURNOVER_OR_OTHER_CF.value],
            )
        ) is None:
            return 0.0

        if row[TransactionRegistryColNameValues.SOURCE_FEE.value] is None:
            commission = 0.0
        else:
            commission = cast(
                "float", row[TransactionRegistryColNameValues.SOURCE_FEE.value]
            )

        return turnover_or_other_cf + commission

    @staticmethod
    def calculate_cash_flow_gross_fee_nominal(row: pd.DataFrame) -> float:
        """Calculate nominal total cash flow, excluding fees, for a transaction."""
        if (
            turnover_or_other_cf := cast(
                "float | None",
                row[TransactionRegistryColNameValues.CALC_TURNOVER_OR_OTHER_CF.value],
            )
        ) is None:
            return 0.0

        return turnover_or_other_cf

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
        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] in [
            TransactionTypeValues.CASHBACK.value,
            TransactionTypeValues.FEE.value,
        ]:
            amount = row[ColumnNameValues.AMOUNT.value]
        else:
            amount = (
                row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
                * row[TransactionRegistryColNameValues.SOURCE_PRICE.value]
            )

        # Buy and tax is a negative cash flow for us
        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] in [
            TransactionTypeValues.BUY.value,
            TransactionTypeValues.TAX.value,
            TransactionTypeValues.FEE.value,
        ]:
            amount = abs(amount) * -1
        else:
            amount = abs(amount)

        return cast("float", amount)

    @staticmethod
    def normalize_no_traded(row: pd.DataFrame) -> float:
        """
        Calculate number of units traded.

        We expect this number to be positive and use the type (buy/sell) to indicate
        the direction of the flow.
        """
        no_traded = cast(
            "float", row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
        )

        return abs(no_traded)

    @staticmethod
    def normalize_fx(row: pd.DataFrame) -> float:
        """Return FX rate or default to 1.00."""
        if TransactionRegistryColNameValues.SOURCE_FX.value not in row or pd.isna(
            row[TransactionRegistryColNameValues.SOURCE_FX.value]
        ):
            return 1.00

        return cast("float", row[TransactionRegistryColNameValues.SOURCE_FX.value])

    @staticmethod
    def calculate_adjusted_price_per_unit(group: pd.DataFrame) -> pd.DataFrame:
        """Calculate adjusted price per unit."""
        group[TransactionRegistryColNameValues.INTERNAL_TURNOVER.value] = group.apply(
            lambda x: (
                (
                    x[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
                    == TransactionTypeValues.BUY.value
                )
                - (
                    x[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
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
            # We only want to apply the logic to buy and sell transactions
            if row[
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value
            ] not in [
                TransactionTypeValues.BUY.value,
                TransactionTypeValues.SELL.value,
            ]:
                continue

            current_turnover += row[
                TransactionRegistryColNameValues.INTERNAL_TURNOVER.value
            ]

            group.at[  # noqa: PD008
                index,
                TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value,
            ] = False

            if (
                row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
                == TransactionTypeValues.BUY.value
            ):
                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ] = (
                    current_turnover
                    / row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
                )

            if (
                row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
                == TransactionTypeValues.SELL.value
            ):
                # When selling the last remaining holdings, the last_entry_price
                # will be 0 and we should return None
                if isinstance(last_entry_price, pd.Series):
                    return_value = (
                        None if last_entry_price.iloc[0] else last_entry_price
                    )
                else:
                    return_value = None if last_entry_price == 0.0 else last_entry_price

                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ] = return_value

            # There might be fractional rounding errors when closing a position so we
            # guard against that here
            if (
                round(
                    row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value],
                    0,
                )
                == 0
            ):
                # We keep current value of PRICE_PER_UNIT here as it might be used
                # in calculating PnL
                current_turnover = 0.0
                group.at[  # noqa: PD008
                    index,
                    TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value,
                ] = None
                group.at[  # noqa: PD008
                    index, TransactionRegistryColNameValues.INTERNAL_TURNOVER.value
                ] = None
                group.at[  # noqa: PD008
                    index,
                    TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value,
                ] = True

            last_entry_price = group.at[  # noqa: PD008
                index, TransactionRegistryColNameValues.PRICE_PER_UNIT.value
            ]

        return group

    @staticmethod
    def cleanup_price_per_unit(row: pd.DataFrame) -> float | None:
        """Set average price per unit to None when applicable."""
        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] in [
            TransactionTypeValues.DIVIDEND.value,
        ]:
            return None

        if row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value] is None:
            return None

        if round(
            row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value],
            0,
        ) == 0 or pd.isna(
            row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
        ):
            return None

        return cast("float", row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value])

    @staticmethod
    def cleanup_quantity_held(row: pd.DataFrame) -> float | None:
        """Set adjusted quantity held to None when applicable."""
        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] in [
            TransactionTypeValues.DIVIDEND.value,
        ]:
            return None

        if row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value] is None:
            return None

        return cast(
            "float", row[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value]
        )


class PandasAlgorithmPnL:
    """Pandas algorithm for PnL transaction data."""

    @staticmethod
    def calculate_pnl_trade(row: pd.DataFrame) -> float | None:
        """Calculate profit and loss from a trade."""
        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] not in [
            TransactionTypeValues.SELL.value,
        ]:
            return None

        commission = float(
            row.get(TransactionRegistryColNameValues.SOURCE_FEE.value, 0.0)
        )

        if pd.isna(commission):
            commission = 0.0

        if (
            TransactionRegistryColNameValues.SOURCE_PRICE.value not in row
            or TransactionRegistryColNameValues.PRICE_PER_UNIT.value not in row
            or TransactionRegistryColNameValues.SOURCE_VOLUME.value not in row
        ):
            transaction_result = 0.0
        else:
            transaction_result = float(
                (
                    row[TransactionRegistryColNameValues.SOURCE_PRICE.value]
                    - row[TransactionRegistryColNameValues.PRICE_PER_UNIT.value]
                )
                * row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
            )

        return transaction_result + commission

    @staticmethod
    def calculate_pnl_dividend(row: pd.DataFrame) -> float | None:
        """Calculate profit and loss from a dividend."""
        if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value] not in [
            TransactionTypeValues.DIVIDEND.value,
        ]:
            return None

        if (
            TransactionRegistryColNameValues.SOURCE_PRICE.value not in row
            or TransactionRegistryColNameValues.SOURCE_VOLUME.value not in row
        ):
            return None

        return float(
            row[TransactionRegistryColNameValues.SOURCE_PRICE.value]
            * row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
        )

    @staticmethod
    def calculate_pnl_total(row: pd.DataFrame) -> float:
        """Calculate total profit and loss."""
        if (
            pd.isna(row[TransactionRegistryColNameValues.CALC_PNL_TRADE.value])
            or row[TransactionRegistryColNameValues.CALC_PNL_TRADE.value] is None
        ):
            pnl_trade = 0.0
        else:
            pnl_trade = cast(
                "float", row[TransactionRegistryColNameValues.CALC_PNL_TRADE.value]
            )

        if (
            pd.isna(row[TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value])
            or row[TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value] is None
        ):
            pnl_dividend = 0.0
        else:
            pnl_dividend = cast(
                "float", row[TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value]
            )

        return pnl_dividend + pnl_trade
