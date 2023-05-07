"""Utils."""
import math
import re
from typing import cast

import pandas as pd

from pypmanager.loader_transaction.const import TransactionTypeValues

EMPTY_COLUMNS = [
    "cumulative_buy_amount",
    "cumulative_buy_volume",
    "cumulative_dividends",
    "cumulative_fees",
    "cumulative_interest",
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
    df_calculations = data.copy()

    for col in EMPTY_COLUMNS:
        df_calculations[col] = 0.0

    df_calculations["average_price"] = None

    cumulative_buy_amount: float = 0.0
    cumulative_buy_volume: float = 0.0
    cumulative_dividends: float = 0.0
    cumulative_fees: float = 0.0
    cumulative_interest: float = 0.0
    cumulative_invested_amount: float = 0.0
    average_price: float | None = 0.0
    realized_pnl: float | None = 0.0

    # Loop through all rows
    for index, row in df_calculations.iterrows():
        amount = cast(float, row["amount"])
        no_traded = cast(float, abs(row["no_traded"]))
        commission = cast(float, abs(row["commission"]))
        transaction_type = cast(str, row["transaction_type"])

        if transaction_type == TransactionTypeValues.INTEREST.value:
            realized_pnl = amount
            cumulative_interest += amount

        if transaction_type == TransactionTypeValues.DIVIDEND.value:
            realized_pnl = amount
            cumulative_dividends += amount

        if transaction_type == TransactionTypeValues.TAX.value:
            realized_pnl = +amount

        if transaction_type == TransactionTypeValues.FEE.value:
            realized_pnl = amount
            cumulative_fees += amount

        if transaction_type == TransactionTypeValues.BUY.value:
            cumulative_buy_volume += no_traded
            # Amounts have a negative sign due to being cash outflows so we need to
            # adjust for that here
            cumulative_buy_amount += -amount
            # Amount will be negative here due to it being a negative cash flow
            cumulative_invested_amount += -amount + commission
            average_price = cumulative_invested_amount / cumulative_buy_volume
            realized_pnl = None

        if transaction_type == TransactionTypeValues.SELL.value:
            cumulative_invested_amount += -amount
            cumulative_buy_volume += -no_traded
            realized_pnl = (row["price"] - average_price) * no_traded - commission

        if math.isclose(cumulative_buy_volume, 0, rel_tol=1e-9, abs_tol=1e-12):
            cumulative_buy_volume = 0.0
            average_price = None
            cumulative_invested_amount = 0.0
            cumulative_buy_amount = 0.0

        # Save the correct state
        df_calculations.loc[index, "cumulative_buy_amount"] = cumulative_buy_amount
        df_calculations.loc[index, "cumulative_buy_volume"] = cumulative_buy_volume
        df_calculations.loc[index, "cumulative_interest"] = cumulative_interest
        df_calculations.loc[index, "cumulative_fees"] = cumulative_fees
        df_calculations.loc[index, "cumulative_dividends"] = cumulative_dividends
        df_calculations.loc[index, "average_price"] = average_price
        df_calculations.loc[index, "realized_pnl"] = realized_pnl
        df_calculations.loc[
            index, "cumulative_invested_amount"
        ] = cumulative_invested_amount

    return df_calculations
