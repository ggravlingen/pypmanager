"""Handle securities."""
from dataclasses import dataclass
from datetime import date, datetime
import logging
import math
from typing import cast

import pandas as pd

from pypmanager.const import NUMBER_FORMATTER
from pypmanager.loader_transaction.const import TransactionTypeValues
from pypmanager.security import MutualFund

LOGGER = logging.Logger(__name__)

EMPTY_COLUMNS = [
    "cumulative_buy_amount",
    "cumulative_buy_volume",
    "cumulative_dividends",
    "cumulative_interest",
    "realized_pnl",
    "cumulative_invested_amount",
]


def _calculate_aggregates(data: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
    """Calculate aggregate values for a holding."""
    df = data.copy()

    for col in EMPTY_COLUMNS:
        df[col] = 0.0

    df["average_price"] = None

    cumulative_buy_amount: float = 0.0
    cumulative_buy_volume: float = 0.0
    cumulative_dividends: float = 0.0
    cumulative_interest: float = 0.0
    cumulative_invested_amount: float = 0.0
    average_price: float | None = 0.0
    realized_pnl: float | None = 0.0

    for index, row in df.iterrows():
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
        df.at[index, "cumulative_buy_amount"] = cumulative_buy_amount
        df.at[index, "cumulative_buy_volume"] = cumulative_buy_volume
        df.at[index, "cumulative_interest"] = cumulative_interest
        df.at[index, "cumulative_dividends"] = cumulative_dividends
        df.at[index, "average_price"] = average_price
        df.at[index, "realized_pnl"] = realized_pnl
        df.at[index, "cumulative_invested_amount"] = cumulative_invested_amount

    return df


@dataclass
class Holding:
    """Represent a security."""

    all_data: pd.DataFrame
    name: str
    calculated_data: pd.DataFrame | None = None
    report_date: datetime | None = None

    def __post_init__(self) -> None:
        """
        Run after class has been instantiated.

        Here, we filter the data on security name and, if applicable, report date.
        """
        df = self.all_data.query(f"name == '{self.name}'")

        if self.report_date is not None:
            df = df.query(f"index <= '{self.report_date}'")

        self.all_data = df
        self.calculate_values()

    @property
    def security_info(self) -> MutualFund:
        """Return information on the security."""
        return MutualFund(
            isin_code=self.isin_code,
            name=self.name,
            report_date=self.report_date,
        )

    def calculate_values(self) -> None:
        """Calculate all values in the dataframe."""
        self.calculated_data = _calculate_aggregates(
            data=self.all_data,
        )

    @property
    def isin_code(self) -> str | None:
        """Return the security's ISIN code."""
        if self.calculated_data is None:
            return None

        try:
            val = self.calculated_data.isin_code.unique()[0]

            if pd.isna(val) or val == "0":
                return None

            return f"{val}"
        except (IndexError, AttributeError, TypeError):
            return None

    @property
    def current_price(self) -> float | None:
        """Return current price."""
        return self.security_info.nav

    @property
    def date_market_value(self) -> date | None:
        """Return date of valuation."""
        return self.security_info.nav_date

    @property
    def current_holdings(self) -> float | None:
        """Return the number of securities currently held."""
        if (
            self.calculated_data is None
            or self.calculated_data.cumulative_buy_volume.empty
        ):
            return None

        current = self.calculated_data.cumulative_buy_volume.iloc[-1]

        # We use round here as no sold/bought may not sum to exactly 0 when divesting
        if math.isclose(current, 0, rel_tol=1e-9, abs_tol=1e-12):
            return None

        if pd.isna(current):
            return None

        return cast(float, current)

    @property
    def total_transactions(self) -> int:
        """Return the total number of transactions made."""
        if self.calculated_data is None:
            return 0

        return len(self.calculated_data)

    @property
    def date_last_transaction(self) -> date | None:
        """Return last transaction date."""
        if self.calculated_data is None:
            return None

        return cast(date, max(self.calculated_data.index))

    @property
    def date_first_transaction(self) -> date | None:
        """Return last transaction date."""
        if self.calculated_data is None:
            return None

        return cast(date, min(self.calculated_data.index))

    @property
    def average_price(self) -> float | None:
        """Return average price."""
        if self.calculated_data is None or self.calculated_data.average_price.empty:
            return 0.0

        if (avg_price := self.calculated_data.average_price.iloc[-1]) is None:
            return None

        return cast(float, avg_price)

    @property
    def dividends(self) -> float | None:
        """Return average price."""
        if (
            self.calculated_data is None
            or self.calculated_data.cumulative_dividends.empty
        ):
            return None

        if (
            dividends := self.calculated_data.cumulative_dividends.iloc[-1]
        ) is None or dividends == 0:
            return None

        return cast(float, dividends)

    @property
    def interest(self) -> float | None:
        """Return average price."""
        if (
            self.calculated_data is None
            or self.calculated_data.cumulative_interest.empty
        ):
            return None

        if (
            dividends := self.calculated_data.cumulative_interest.iloc[-1]
        ) is None or dividends == 0:
            return None

        return cast(float, dividends)

    @property
    def market_value(self) -> float | None:
        """Return current market value."""
        if self.current_price is None or self.current_holdings is None:
            return None

        if (market_value := self.current_price * self.current_holdings) == 0:
            return None

        return market_value

    @property
    def realized_pnl(self) -> float:
        """Return realized PnL."""
        if self.calculated_data is None or self.calculated_data.realized_pnl.empty:
            return 0.0

        pnl = self.calculated_data.realized_pnl.sum()

        if pd.isna(pnl):
            return 0.0

        return cast(float, pnl)

    @property
    def unrealized_pnl(self) -> float | None:
        """Return unrealized PnL."""
        if (
            self.average_price is None
            or self.current_price is None
            or self.current_holdings is None
        ):
            return 0.0

        return (self.current_price - self.average_price) * self.current_holdings

    @property
    def total_pnl(self) -> float | None:
        """Return PnL."""
        if self.unrealized_pnl is None or self.realized_pnl is None:
            return None

        return self.realized_pnl + self.unrealized_pnl

    @property
    def invested_amount(self) -> float | None:
        """Return total invested amount."""
        if self.average_price is None or self.current_holdings is None:
            return None

        calc_val = self.average_price * self.current_holdings

        if round(calc_val) == 0:
            return None

        return calc_val

    @property
    def cli_table_row(self) -> list[str | None]:
        """Represent the holding for CLI reports."""
        invested_amount = (
            f"{self.invested_amount:{NUMBER_FORMATTER}}"
            if self.invested_amount
            else None
        )

        market_value = (
            f"{self.market_value:{NUMBER_FORMATTER}}" if self.market_value else None
        )

        return [
            self.name,
            invested_amount,
            market_value,
            f"{self.total_pnl:{NUMBER_FORMATTER}}",
            f"{self.realized_pnl:{NUMBER_FORMATTER}}",
            f"{self.unrealized_pnl:{NUMBER_FORMATTER}}",
            f"{self.date_market_value}",
            f"{self.total_transactions}",
        ]
