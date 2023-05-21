"""Calculation tools for aggregates."""
import logging
import math
import re
from typing import Any, cast

import pandas as pd

from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues

LOGGER = logging.Logger(__name__)

CALCULATED_COLUMNS = [
    "average_fx_rate",
    "average_price",
    "cash_flow_base_ccy",
    "cumulative_invested_amount",
    "cumulative_buy_amount",
    "cumulative_buy_volume",
    "cumulative_interest",
    "cumulative_dividends",
    "cumulative_fees",
    "realized_pnl",
    "realized_pnl_equity",
    "realized_pnl_fx",
]


def to_valid_column_name(name: str) -> str:
    """Convert a string to a valid pandas column name."""
    name = name.lower()  # lowercase

    name = re.sub(r"\s+", "_", name)  # replace whitespace with underscores

    name = re.sub(r"[^\w]", "", name)  # remove non-alphanumeric characters

    if (
        not name[0].isalpha() and name[0] != "_"
    ):  # ensure column name starts with a letter or underscore
        name = "_" + name

    return name


def _calculate_cash_flow(row: dict[str, Any]) -> float:
    """Calculate FX-adjusted cash flow."""
    amount = cast(float, row[ColumnNameValues.AMOUNT])

    # Convert amount to base currency
    if ColumnNameValues.FX in row and row[ColumnNameValues.FX]:
        fx_rate = cast(float, row[ColumnNameValues.FX])
        amount *= fx_rate

    commission = cast(float, row[ColumnNameValues.COMMISSION])
    if commission is None or pd.isna(commission):
        commission = 0.0

    return amount + commission


def calculate_aggregates(data: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
    """Calculate aggregate values for a holding."""
    data_copy = data.copy()

    data_copy[
        ColumnNameValues.TRANSACTION_DATE
    ] = data_copy.index  # Convert index to a column
    data_list = data_copy.to_dict("records", index=True)

    average_fx_rate: float | None = 0.0
    average_price: float | None = 0.0
    cash_flow_base_ccy: float = 0.0
    cumulative_buy_amount: float = 0.0
    cumulative_buy_volume: float = 0.0
    cumulative_dividends: float = 0.0
    cumulative_fees: float = 0.0
    cumulative_interest: float = 0.0
    cumulative_invested_amount: float = 0.0
    sum_amount_x_fx: float = 0.0
    realized_pnl: float | None = 0.0  # pylint: disable=possibly-unused-variable
    realized_pnl_equity: float = 0.0  # pylint: disable=possibly-unused-variable
    realized_pnl_fx: float = 0.0  # pylint: disable=possibly-unused-variable

    # Loop through all rows
    output_data: list[dict[str, Any]] = []
    for row in data_list:
        if math.isclose(cumulative_buy_volume, 0, rel_tol=1e-9, abs_tol=1e-12):
            LOGGER.debug(
                f"Cumulative buy volume too small {cumulative_buy_volume} for "
                f"{row['transaction_type']}"
            )
            cumulative_buy_volume = 0.0
            cumulative_invested_amount = 0.0
            cumulative_buy_amount = 0.0

        amount = cast(float, row[ColumnNameValues.AMOUNT])  # in nominal amount
        cash_flow_base_ccy = _calculate_cash_flow(row=row)
        commission = cast(float | None, abs(row[ColumnNameValues.COMMISSION]))
        no_traded = cast(float, abs(row[ColumnNameValues.NO_TRADED]))
        transaction_type = cast(str, row[ColumnNameValues.TRANSACTION_TYPE])

        if ColumnNameValues.FX in row:
            fx_rate = cast(float, abs(row[ColumnNameValues.FX]))
        else:
            fx_rate = 1.0
        if pd.isna(fx_rate):
            fx_rate = 1.0

        if transaction_type == TransactionTypeValues.INTEREST.value:
            realized_pnl = amount
            cumulative_interest += amount

        if transaction_type == TransactionTypeValues.DIVIDEND.value:
            realized_pnl = amount
            cumulative_dividends += amount

        if transaction_type in [
            TransactionTypeValues.TAX.value,
            TransactionTypeValues.CASHBACK.value,
        ]:
            realized_pnl = +amount

        if transaction_type == TransactionTypeValues.FEE.value:
            realized_pnl = amount
            cumulative_fees += amount

        if transaction_type == TransactionTypeValues.FEE_CREDIT.value:
            realized_pnl = amount
            cumulative_fees += amount

        if transaction_type == TransactionTypeValues.BUY.value:
            cumulative_buy_volume += no_traded

            # Amounts have a negative sign due to being cash outflows so we need to
            # adjust for that here
            cumulative_buy_amount += -amount

            # Calculate volume weighted fx rate
            sum_amount_x_fx += -amount * fx_rate

            # Amount will be negative here due to it being a negative cash flow
            cumulative_invested_amount += cash_flow_base_ccy
            try:
                average_price = cumulative_invested_amount / cumulative_buy_volume * -1
            except ZeroDivisionError:
                average_price = None

            try:
                average_fx_rate = sum_amount_x_fx / cumulative_buy_amount
            except ZeroDivisionError:
                average_fx_rate = None

            realized_pnl = None

        if transaction_type == TransactionTypeValues.SELL.value:
            cumulative_invested_amount += cash_flow_base_ccy
            cumulative_buy_volume += -no_traded

            assert average_price is not None

            # Calculate PnL
            realized_pnl_equity = (
                (row[ColumnNameValues.PRICE] - average_price)
                * no_traded
                * average_fx_rate
            ) - commission

            realized_pnl_fx = (
                (row[ColumnNameValues.FX] - average_fx_rate)
                * (average_price * no_traded)
                * average_fx_rate
            )

            realized_pnl = realized_pnl_equity + realized_pnl_fx

        if math.isclose(cumulative_buy_volume, 0, rel_tol=1e-9, abs_tol=1e-12):
            LOGGER.debug(
                f"Cumulative buy volume too small {cumulative_buy_volume} for "
                f"{row['transaction_type']}"
            )
            average_fx_rate = 0.0
            average_price = None

        # All variables defined inside this function
        _locals = locals()

        # Save the correct state
        for field in CALCULATED_COLUMNS:
            row[field] = _locals[field]

        output_data.append(row)

    return pd.DataFrame(output_data).set_index(ColumnNameValues.TRANSACTION_DATE)


def calculate_results(data: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
    """Calculate aggregate values for a holding."""
    all_securities_name = cast(list[str], data.name.unique())

    dfs: list[pd.DataFrame] = []

    for name in all_securities_name:
        df_data = data.query(f"name == '{name}'")
        df_result = calculate_aggregates(df_data)

        dfs.append(df_result)

    df_output = pd.concat(dfs, ignore_index=False)

    return df_output
