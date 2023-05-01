"""Representation of a security."""
from datetime import date
from typing import cast

import pandas as pd


class MutualFund:
    """A mutual fund."""

    filtered_df: pd.DataFrame | None

    def __init__(self, isin_code: str | None = None, name: str | None = None) -> None:
        """Init."""
        self.isin_code = isin_code
        self.name = name

        self._load_data()

    def _load_data(self) -> None:
        """Load market data."""
        df = pd.read_csv("data/market_data.csv", sep=";")
        if not pd.isna(self.isin_code):
            df_filtered = df.query(f"isin_code == '{self.isin_code}'")
        else:
            df_filtered = df.query(f"name == '{self.name}'")

        self.filtered_df = df_filtered

    @property
    def nav(self) -> float | None:
        """Return net asset value."""
        try:
            if self.filtered_df is None:
                return None

            val = self.filtered_df["price"].values[0]

            if pd.isna(val):
                return None

            return cast(float, val)
        except IndexError:
            return None

    @property
    def nav_date(self) -> date | None:
        """Return date of net asset value."""
        if self.filtered_df is None:
            return None

        try:
            val = self.filtered_df["report_date"].values[0]

            if pd.isna(val):
                return None

            return cast(date, val)
        except IndexError:
            return None
