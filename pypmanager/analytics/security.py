"""Representation of a security."""

from datetime import date
from typing import cast

import pandas as pd

from pypmanager.settings import Settings


class MutualFund:
    """A mutual fund."""

    filtered_df: pd.DataFrame | None

    def __init__(
        self,
        isin_code: str | None = None,
        name: str | None = None,
        report_date: date | None = None,
    ) -> None:
        """Init."""
        self.isin_code = isin_code
        self.name = name
        self.report_date = report_date

        self._load_data()

    def _load_data(self) -> None:
        """Load market data."""
        df_market_data = pd.read_csv(
            Settings.file_market_data, sep=";", index_col="report_date"
        )

        if self.isin_code:
            df_filtered = df_market_data.query(f"isin_code == '{self.isin_code}'")
        else:
            df_filtered = df_market_data.query(f"name == '{self.name}'")

        self.filtered_df = df_filtered.sort_values("report_date")

    @property
    def _last_row(self) -> pd.DataFrame:
        """Return last row."""
        if self.nav_date is None or self.filtered_df is None:
            return pd.DataFrame()

        return self.filtered_df.query(f"report_date == '{self.nav_date}'")

    @property
    def nav(self) -> float | None:
        """Return net asset value."""
        try:
            if self.filtered_df is None or self.nav_date is None:
                return None

            val = self._last_row["price"].to_numpy()[0]

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
            if self.report_date is not None:
                val = self.filtered_df.query(
                    f"index <= '{self.report_date}'"
                ).index.max()
            else:
                val = self.filtered_df.index.max()

            if pd.isna(val):
                return None

            return cast(date, val)
        except IndexError:
            return None
