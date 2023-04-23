"""Handle securities."""
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from pypmanager.data_loader import TransactionTypeValues
from pypmanager.market_price import MarketPrice

market_price = MarketPrice()


@dataclass
class Security:
    """Represent a security."""

    name: str
    all_data: pd.DataFrame
    calculated_data: pd.DataFrame | None = None

    def __post_init__(self):
        """Run after class has been instantiate."""
        self.calculate_values()

    def calculate_values(self) -> None:
        """Calculate all values in the dataframe."""
        df = self.all_data.query(f"name == '{self.name}'").sort_index()

        df["current_holdings"] = 0.0
        df["cumulative_buy_amount"] = 0.0
        df["cumulative_buy_volume"] = 0.0
        df["average_cost_basis"] = 0.0
        df["realized_pnl"] = 0.0
        df["cumulative_invested_amount"] = 0.0

        # Iterate through the rows and update the new columns
        current_holdings = 0.0
        cumulative_buy_amount = 0.0
        cumulative_buy_volume = 0.0
        cumulative_invested_amount = 0.0
        average_price = 0.0

        for index, row in df.iterrows():
            current_holdings += row["no_traded"]

            if row["transaction_type"] == TransactionTypeValues.BUY.value:
                cumulative_buy_amount += row["amount"]
                cumulative_buy_volume += row["no_traded"]
                cumulative_invested_amount += row["amount"] + row["commission"]
                average_price = cumulative_buy_amount / cumulative_buy_volume
                realized_pnl = None
            else:
                realized_pnl = (row["price"] - average_price) * row[
                    "no_traded"
                ] * -1 - abs(row["commission"])

            if current_holdings == 0:
                average_price = None

            df.at[index, "cumulative_buy_amount"] = cumulative_buy_amount
            df.at[index, "cumulative_buy_volume"] = cumulative_buy_volume
            df.at[index, "average_price"] = average_price
            df.at[index, "realized_pnl"] = realized_pnl
            df.at[index, "cumulative_invested_amount"] = cumulative_invested_amount
            df.at[index, "current_holdings"] = current_holdings

        self.calculated_data = df

    @property
    def isin_code(self) -> str:
        """Return the security's ISIN code."""
        try:
            return self.calculated_data.isin_code.unique()[0]
        except (IndexError, AttributeError):
            return "No ISIN"

    @property
    def current_price(self) -> float | None:
        """Return current price."""
        try:
            return market_price.lookup_table[self.isin_code]
        except KeyError:
            return None

    @property
    def current_holdings(self) -> float | None:
        """Return the number of securities currently held."""
        if (current := self.calculated_data.current_holdings.iloc[-1]) == 0:
            return None

        return current

    @property
    def total_transactions(self) -> int:
        """Return the total number of transactions made."""
        return len(self.calculated_data)

    @property
    def date_last_transaction(self) -> date:
        """Return last transaction date."""
        return max(self.calculated_data.index)

    @property
    def date_first_transaction(self) -> date:
        """Return last transaction date."""
        return min(self.calculated_data.index)

    @property
    def average_price(self) -> float | None:
        """Return average price."""
        avg_price = self.calculated_data.average_price.iloc[-1]

        if np.isnan(avg_price):
            return None

        return avg_price

    @property
    def market_value(self) -> float | None:
        """Return current market value."""
        if self.current_price is None or self.current_holdings is None:
            return None

        if (market_value := self.current_price * self.current_holdings) == 0:
            return None

        return market_value

    @property
    def realized_pnl(self) -> float | None:
        """Return realized PnL."""
        pnl = self.calculated_data.realized_pnl.iloc[-1]

        if pd.isna(pnl):
            return None

        return pnl

    @property
    def unrealized_pnl(self) -> float | None:
        """Return unrealized PnL."""
        if self.average_price is None or self.current_price is None:
            return None

        return (self.current_price - self.average_price) * self.current_holdings

    @property
    def total_pnl(self) -> float:
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
