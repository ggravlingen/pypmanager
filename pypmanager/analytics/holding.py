"""Handle securities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from functools import cached_property
import logging
import math
from typing import cast

import numpy as np
import pandas as pd

from pypmanager.ingest.transaction import (
    AccountNameValues,
    ColumnNameValues,
    TransactionRegistryColNameValues,
)
from pypmanager.settings import Settings

from .security import MutualFund

LOGGER = logging.getLogger(__name__)


def get_market_data(isin_code: str | None = None) -> pd.DataFrame:
    """
    Load all market data from CSV files and concatenate them into a single DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing all the market data concatenated together,
        indexed by 'report_date'.
    """
    all_data_frames: list[pd.DataFrame] = []

    for file in Settings.dir_market_data.glob("*.csv"):
        df_market_data = pd.read_csv(file, sep=";", index_col="report_date")
        all_data_frames.append(df_market_data)

    merged_df = pd.concat(all_data_frames, ignore_index=False)

    if isin_code:
        return merged_df.query(f"isin_code == '{isin_code}'")

    return merged_df


@dataclass
class Holding:
    """Represent a security."""

    df_general_ledger: pd.DataFrame
    name: str
    calculated_data: pd.DataFrame | None = None
    report_date: datetime | None = None

    # Caching
    _security_info: MutualFund | None = None

    def __repr__(self: Holding) -> str:
        """Representation of class."""
        return f"{self.name} | {self.current_holdings}"

    def __post_init__(self: Holding) -> None:
        """
        Run after class has been instantiated.

        Here, we filter the data on security name and, if applicable, report date.
        We filter by ledger account = cash since the relevant data is in that row.
        """
        df_all_data = self.df_general_ledger.query(
            f"{TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value} == "
            f"'{self.name}' and ledger_account == '{AccountNameValues.CASH}'",
        )

        if self.report_date is not None:
            report_date_datetime64 = np.datetime64(
                pd.to_datetime(self.report_date.date())
            )
            df_all_data = df_all_data.loc[(df_all_data.index <= report_date_datetime64)]

        self.df_general_ledger = df_all_data

        self.calculated_data = df_all_data

    @cached_property
    def df_market_data(self: Holding) -> pd.DataFrame:
        """Return market data."""
        return get_market_data()

    @cached_property
    def current_holdings(self: Holding) -> float | None:
        """
        Return the number of securities currently held.

        Will return None if everything has been sold.
        """
        if self.calculated_data is None:
            return None

        total_held = self.calculated_data[
            TransactionRegistryColNameValues.SOURCE_VOLUME
        ].sum()

        if (
            self.calculated_data is None
            or pd.isna(total_held)
            or math.isclose(total_held, 0, rel_tol=1e-9, abs_tol=1e-12)
        ):
            return None

        return cast(float, total_held)

    @cached_property
    def security_info(self: Holding) -> MutualFund:
        """Return information on the security."""
        if self._security_info is None:  # Hit these calculations only once
            self._security_info = MutualFund(
                df_market_data=self.df_market_data,
                isin_code=self.isin_code,
                name=self.name,
                report_date=self.report_date,
            )

        return self._security_info

    @cached_property
    def current_price(self: Holding) -> float | None:
        """Return current price."""
        if self.current_holdings is None:
            return None

        return self.security_info.nav

    @property
    def date_market_value(self: Holding) -> date | None:
        """Return date of valuation."""
        if self.current_holdings is None:
            return None

        return self.security_info.nav_date

    @cached_property
    def isin_code(self: Holding) -> str | None:
        """Return the security's ISIN code."""
        if self.calculated_data is None:
            return None

        try:
            val = self.calculated_data[
                TransactionRegistryColNameValues.SOURCE_ISIN
            ].unique()[0]
        except (IndexError, AttributeError, TypeError):
            return None

        if pd.isna(val) or val == "0":
            return None

        return f"{val}"

    @property
    def total_transactions(self: Holding) -> int:
        """Return the total number of transactions made."""
        if self.calculated_data is None:
            return 0

        return len(self.calculated_data)

    @property
    def date_last_transaction(self: Holding) -> date | None:
        """Return last transaction date."""
        if self.calculated_data is None:
            return None

        return cast(date, max(self.calculated_data.index))

    @property
    def date_first_transaction(self: Holding) -> date | None:
        """Return last transaction date."""
        if self.calculated_data is None:
            return None

        return cast(date, min(self.calculated_data.index))

    @property
    def average_fx_rate(self: Holding) -> float | None:
        """Return average price."""
        if self.calculated_data is None or self.calculated_data.average_fx_rate.empty:
            return 0.0

        if (average_fx_rate := self.calculated_data.average_fx_rate.iloc[-1]) is None:
            return None

        return cast(float, average_fx_rate)

    @cached_property
    def average_price(self: Holding) -> float | None:
        """Return average price."""
        if (
            self.calculated_data is None
            or self.calculated_data[ColumnNameValues.AVG_PRICE].empty
        ):
            return 0.0

        avg_price = self.calculated_data[ColumnNameValues.AVG_PRICE].iloc[-1]

        if avg_price is None or pd.isna(avg_price):
            return None

        return cast(float, avg_price)

    @property
    def return_pct(self: Holding) -> float | None:
        """Return return in %."""
        if self.average_price and self.current_price:
            return self.current_price / self.average_price - 1

        return None

    @property
    def dividends(self: Holding) -> float | None:
        """Return dividends price."""
        if (
            self.calculated_data is None
            or self.calculated_data[ColumnNameValues.REALIZED_PNL_DIVIDEND].empty
        ):
            return None

        pnl = self.calculated_data[ColumnNameValues.REALIZED_PNL_DIVIDEND].sum()

        if pd.isna(pnl) or pnl == 0.0:
            return None

        return cast(float, pnl)

    @property
    def fees(self: Holding) -> float | None:
        """Return fees paid."""
        return None

    @property
    def interest(self: Holding) -> float | None:
        """Return interest price."""
        if (
            self.calculated_data is None
            or self.calculated_data[ColumnNameValues.REALIZED_PNL_INTEREST].empty
        ):
            return None

        pnl = self.calculated_data[ColumnNameValues.REALIZED_PNL_INTEREST].sum()

        if pd.isna(pnl) or pnl == 0.0:
            return None

        return cast(float, pnl)

    @property
    def market_value(self: Holding) -> float | None:
        """Return current market value."""
        if self.current_price is None or self.current_holdings is None:
            return None

        if (market_value := self.current_price * self.current_holdings) == 0:
            return None

        return market_value

    @property
    def realized_pnl_equity(self: Holding) -> float:
        """Return realized PnL."""
        if (
            self.calculated_data is None
            or self.calculated_data[ColumnNameValues.REALIZED_PNL_EQ].empty
        ):
            return 0.0

        pnl = self.calculated_data[ColumnNameValues.REALIZED_PNL_EQ].sum()

        if pd.isna(pnl):
            return 0.0

        return cast(float, pnl)

    @property
    def realized_pnl_fx(self: Holding) -> float:
        """Return realized PnL."""
        return 0

    @cached_property
    def realized_pnl(self: Holding) -> float:
        """Return realized PnL."""
        if (
            self.calculated_data is None
            or self.calculated_data[ColumnNameValues.REALIZED_PNL].empty
        ):
            return 0.0

        pnl = self.calculated_data[ColumnNameValues.REALIZED_PNL].sum()

        return cast(float, pnl)

    @cached_property
    def unrealized_pnl(self: Holding) -> float:
        """Return unrealized PnL."""
        if (
            self.average_price is None
            or self.current_price is None
            or self.current_holdings is None
        ):
            return 0.0

        return (self.current_price - self.average_price) * self.current_holdings

    @property
    def total_pnl(self: Holding) -> float:
        """Return PnL."""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def invested_amount(self: Holding) -> float | None:
        """Return total invested amount."""
        if self.average_price is None or self.current_holdings is None:
            return None

        calc_val = self.average_price * self.current_holdings

        if round(calc_val) == 0:
            return None

        return calc_val
