"""Calculation tools for aggregates."""
import logging
import math
import re
from typing import Any, cast

import pandas as pd

from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues

LOGGER = logging.Logger(__name__)

CALCULATED_COLUMNS = [
    "average_price",
    "cumulative_buy_amount",
    "cumulative_buy_volume",
    "cumulative_interest",
    "cumulative_dividends",
    "cumulative_fees",
    "realized_pnl",
    "cumulative_invested_amount",
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


def calculate_aggregates(data: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
    """Calculate aggregate values for a holding."""
    data_copy = data.copy()

    data_copy[
        ColumnNameValues.TRANSACTION_DATE
    ] = data_copy.index  # Convert index to a column
    data_list = data_copy.to_dict("records", index=True)

    cumulative_buy_amount: float = 0.0
    cumulative_buy_volume: float = 0.0
    cumulative_dividends: float = 0.0
    cumulative_fees: float = 0.0
    cumulative_interest: float = 0.0
    cumulative_invested_amount: float = 0.0
    average_price: float | None = 0.0
    realized_pnl: float | None = 0.0  # pylint: disable=possibly-unused-variable

    # Loop through all rows
    output_data: list[dict[str, Any]] = []
    for row in data_list:
        if math.isclose(cumulative_buy_volume, 0, rel_tol=1e-9, abs_tol=1e-12):
            LOGGER.debug(
                f"Cumulative buy volume too small {cumulative_buy_volume} for "
                f"{row['transaction_type']}"
            )
            cumulative_buy_volume = 0.0
            average_price = None
            cumulative_invested_amount = 0.0
            cumulative_buy_amount = 0.0

        amount = cast(float, row[ColumnNameValues.AMOUNT])
        no_traded = cast(float, abs(row[ColumnNameValues.NO_TRADED]))
        commission = cast(float | None, abs(row[ColumnNameValues.COMMISSION]))
        transaction_type = cast(str, row[ColumnNameValues.TRANSACTION_TYPE])

        if commission is None or pd.isna(commission):
            commission = 0

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
            # Amount will be negative here due to it being a negative cash flow
            cumulative_invested_amount += -amount + commission
            try:
                average_price = cumulative_invested_amount / cumulative_buy_volume
            except ZeroDivisionError:
                average_price = None
            realized_pnl = None

        if transaction_type == TransactionTypeValues.SELL.value:
            cumulative_invested_amount += -amount
            cumulative_buy_volume += -no_traded
            realized_pnl = (
                row[ColumnNameValues.PRICE] - average_price
            ) * no_traded - commission

        # All variables defined inside this function
        _locals = locals()

        # Save the correct state
        for field in CALCULATED_COLUMNS:
            row[field] = _locals[field]

        output_data.append(row)

    final_df = pd.DataFrame(output_data)
    final_df = final_df.set_index(ColumnNameValues.TRANSACTION_DATE)

    return final_df


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
