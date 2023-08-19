"""Handle securities."""
from dataclasses import dataclass
from datetime import date
from functools import cached_property
import logging
import math
from typing import cast

import pandas as pd

from pypmanager.loader_transaction.const import AccountNameValues, ColumnNameValues

from .security import MutualFund

LOGGER = logging.Logger(__name__)


@dataclass
class Holding:
    """Represent a security."""

    df_general_ledger: pd.DataFrame
    name: str
    calculated_data: pd.DataFrame | None = None
    report_date: date | None = None

    # Caching
    _security_info: MutualFund | None = None

    def __repr__(self) -> str:
        """Representation of class."""
        return f"{self.name} | {self.current_holdings}"

    def __post_init__(self) -> None:
        """
        Run after class has been instantiated.

        Here, we filter the data on security name and, if applicable, report date.
        We filter by ledger account = cash since the relevant data is in that row.
        """
        df_all_data = self.df_general_ledger.query(
            f"name == '{self.name}' and ledger_account == '{AccountNameValues.CASH}'"
        )

        if self.report_date is not None:
            df_all_data = df_all_data.loc[(df_all_data.index <= self.report_date)]

        self.df_general_ledger = df_all_data

        self.calculated_data = df_all_data

    @cached_property
    def current_holdings(self) -> float | None:
        """
        Return the number of securities currently held.

        Will return None if everything has been sold.
        """
        if self.calculated_data is None:
            return None

        total_held = self.calculated_data[ColumnNameValues.NO_TRADED].sum()

        if (
            self.calculated_data is None
            or pd.isna(total_held)
            or math.isclose(total_held, 0, rel_tol=1e-9, abs_tol=1e-12)
        ):
            return None

        return cast(float, total_held)

    @cached_property
    def security_info(self) -> MutualFund:
        """Return information on the security."""
        if self._security_info is None:  # Hit these calculations only once
            self._security_info = MutualFund(
                isin_code=self.isin_code,
                name=self.name,
                report_date=self.report_date,
            )

        return self._security_info

    @cached_property
    def current_price(self) -> float | None:
        """Return current price."""
        if self.current_holdings is None:
            return None

        return self.security_info.nav

    @property
    def date_market_value(self) -> date | None:
        """Return date of valuation."""
        if self.current_holdings is None:
            return None

        return self.security_info.nav_date

    @cached_property
    def isin_code(self) -> str | None:
        """Return the security's ISIN code."""
        if self.calculated_data is None:
            return None

        try:
            val = self.calculated_data[ColumnNameValues.ISIN_CODE].unique()[0]

            if pd.isna(val) or val == "0":
                return None

            return f"{val}"
        except (IndexError, AttributeError, TypeError):
            return None

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
    def average_fx_rate(self) -> float | None:
        """Return average price."""
        if self.calculated_data is None or self.calculated_data.average_fx_rate.empty:
            return 0.0

        if (average_fx_rate := self.calculated_data.average_fx_rate.iloc[-1]) is None:
            return None

        return cast(float, average_fx_rate)

    @cached_property
    def average_price(self) -> float | None:
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
    def return_pct(self) -> float | None:
        """Return return in %."""
        if self.average_price and self.current_price:
            return self.current_price / self.average_price - 1

        return None

    @property
    def dividends(self) -> float | None:
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
    def fees(self) -> float | None:
        """Return fees paid."""
        return None

    @property
    def interest(self) -> float | None:
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
    def market_value(self) -> float | None:
        """Return current market value."""
        if self.current_price is None or self.current_holdings is None:
            return None

        if (market_value := self.current_price * self.current_holdings) == 0:
            return None

        return market_value

    @property
    def realized_pnl_equity(self) -> float:
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
    def realized_pnl_fx(self) -> float:
        """Return realized PnL."""
        return 0

    @cached_property
    def realized_pnl(self) -> float:
        """Return realized PnL."""
        if (
            self.calculated_data is None
            or self.calculated_data[ColumnNameValues.REALIZED_PNL].empty
        ):
            return 0.0

        pnl = self.calculated_data[ColumnNameValues.REALIZED_PNL].sum()

        return cast(float, pnl)

    @cached_property
    def unrealized_pnl(self) -> float:
        """Return unrealized PnL."""
        if (
            self.average_price is None
            or self.current_price is None
            or self.current_holdings is None
        ):
            return 0.0

        return (self.current_price - self.average_price) * self.current_holdings

    @property
    def total_pnl(self) -> float:
        """Return PnL."""
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
