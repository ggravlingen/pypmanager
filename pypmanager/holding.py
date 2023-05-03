"""Handle securities."""
from dataclasses import dataclass
from datetime import date
from typing import cast

import pandas as pd

from pypmanager.const import NUMBER_FORMATTER
from pypmanager.data_loader import TransactionTypeValues
from pypmanager.security import MutualFund


def _calculate_aggregates(  # noqa: C901
    data: pd.DataFrame, security_name: str
) -> pd.DataFrame:
    """Calculate aggregate values for a holding."""
    df = data.query(f"name == '{security_name}'").sort_index()

    df["cumulative_buy_amount"] = 0.0
    df["cumulative_buy_volume"] = 0.0
    df["realized_pnl"] = 0.0
    df["cumulative_invested_amount"] = 0.0
    df["average_price"] = None

    cumulative_buy_amount: float | None = 0.0
    cumulative_buy_volume: float | None = 0.0
    cumulative_invested_amount: float | None = 0.0
    average_price: float | None = 0.0

    for index, row in df.iterrows():
        # Reset values to 0
        if cumulative_buy_volume is None:
            cumulative_buy_volume = 0.0

        if cumulative_buy_amount is None:
            cumulative_buy_amount = 0.0

        if cumulative_invested_amount is None:
            cumulative_invested_amount = 0.0

        amount = cast(float, abs(row["amount"]))
        no_traded = cast(float, abs(row["no_traded"]))
        commission = cast(float, abs(row["commission"]))
        transaction_type = row["transaction_type"]

        if transaction_type == TransactionTypeValues.BUY.value:
            cumulative_buy_volume += no_traded
            cumulative_buy_amount += amount
            cumulative_invested_amount += amount + commission
            average_price = cumulative_invested_amount / cumulative_buy_volume
            realized_pnl = None

        if transaction_type == TransactionTypeValues.SELL.value:
            realized_pnl = (row["price"] - average_price) * no_traded - commission
            cumulative_invested_amount -= amount
            cumulative_buy_amount -= amount
            cumulative_buy_volume -= no_traded

        if transaction_type == TransactionTypeValues.INTEREST.value:
            realized_pnl = amount

        if transaction_type == TransactionTypeValues.TAX.value:
            realized_pnl = -amount

        if cumulative_invested_amount < 0:
            cumulative_invested_amount = None

        if cumulative_buy_volume == 0:
            cumulative_buy_volume = None
            average_price = None

        if cumulative_buy_amount < 0:
            cumulative_buy_amount = None

        df.at[index, "cumulative_buy_amount"] = cumulative_buy_amount
        df.at[index, "cumulative_buy_volume"] = cumulative_buy_volume
        df.at[index, "average_price"] = average_price
        df.at[index, "realized_pnl"] = realized_pnl
        df.at[index, "cumulative_invested_amount"] = cumulative_invested_amount

    return df


@dataclass
class Holding:
    """Represent a security."""

    name: str
    all_data: pd.DataFrame
    calculated_data: pd.DataFrame | None = None

    def __post_init__(self) -> None:
        """Run after class has been instantiate."""
        self.calculate_values()

    @property
    def security_info(self) -> MutualFund:
        """Return information on the security."""
        return MutualFund(isin_code=self.isin_code, name=self.name)

    def calculate_values(self) -> None:
        """Calculate all values in the dataframe."""
        self.calculated_data = _calculate_aggregates(
            data=self.all_data, security_name=self.name
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

        if (current := self.calculated_data.cumulative_buy_volume.iloc[-1]) == 0:
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

        return self.average_price * self.current_holdings

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
