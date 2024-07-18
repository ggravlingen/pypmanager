"""Aggregation calculator."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pandas as pd

from pypmanager.ingest.transaction import ColumnNameValues, TransactionTypeValues

if TYPE_CHECKING:
    from datetime import date

LOGGER = logging.getLogger(__name__)


class CalculateAggregates:
    """Class to calculate aggregates for a security."""

    input_data: list[dict[str, Any]]
    calculated_transaction_list: list[dict[str, Any]]
    output_data: pd.DataFrame

    # The transaction's amount
    amount: float | None = None
    # Name of the broker
    broker: str
    # Name of the source
    source: str
    # The date of the transaction
    transaction_date: date
    # Type of transaction, eg buy/sell
    transaction_type: str
    # The FX rate against the base currency
    fx_rate: float
    # Currency of the transaction
    nominal_ccy: str
    # Number of securities traded in the transaction
    no_traded: float | None = None
    # The name of the security
    name: str
    # The name ISIN of the security
    isin: str | None = None
    # The price of the security
    nominal_price: float | None
    # The commission paid. None if there is no commission.
    nominal_commission: float | None = None
    # Cumulative sum of bought/sold. None if all are sold.
    cf_ex_commission: float | None = None
    # The current amount held
    sum_held: float | None = None
    # The total PnL
    pnl_total: float | None = None
    # The PnL from changes in the security price
    pnl_price: float | None = None
    # The PnL from commissions paid
    pnl_commission: float | None = None
    # The PnL from interest paid or received
    pnl_interest: float | None = None
    # The PnL from dividends received
    pnl_dividend: float | None = None
    # The delta on the cost bases from this transaction
    cost_basis_delta: float | None = None
    # The cumulative sum of cost_basis_delta
    sum_cost_basis_delta: float | None = None
    # The average cost for the currently held securities
    avg_cost_basis: float | None = None
    # The transaction's cash flow effect
    transaction_cash_flow: float | None = None
    # The transaction's cash flow effect in the local currency
    transaction_cash_flow_local: float | None = None
    # The year of the transaction
    transaction_year: int

    def __init__(
        self: CalculateAggregates,
        security_transactions: pd.DataFrame,
    ) -> None:
        """Init class."""
        self.calculated_transaction_list = []
        data_copy = security_transactions.copy()
        self.data = data_copy

        # Set the index to a date explicitly
        data_copy.index = pd.to_datetime(data_copy.index)
        data_copy.index = data_copy.index.map(lambda x: x.date())

        data_copy[ColumnNameValues.TRANSACTION_DATE] = (
            data_copy.index
        )  # Convert index to a column

        self.input_data = data_copy.to_dict("records", index=True)

        self.parse_transactions()

        final_df = pd.DataFrame(self.calculated_transaction_list)
        final_df = final_df.set_index(ColumnNameValues.TRANSACTION_DATE)
        self.output_data = final_df

    def parse_transactions(self: CalculateAggregates) -> None:
        """Loop through all transactions."""
        for row in self.input_data:
            self.set_base_data(row=row)

            if self.transaction_type == TransactionTypeValues.INTEREST.value:
                self.handle_interest()

            if self.transaction_type == TransactionTypeValues.DIVIDEND.value:
                self.handle_dividend()

            if self.transaction_type == TransactionTypeValues.BUY.value:
                self.handle_buy()

            if self.transaction_type == TransactionTypeValues.SELL.value:
                self.handle_sell()

            self.calculate_total_pnl()
            self.add_transaction()

    def handle_interest(self: CalculateAggregates) -> None:
        """Handle an interest payment."""
        if self.pnl_interest is None:
            self.pnl_interest = 0.0

        if self.amount:
            self.pnl_interest += self.amount
            self.transaction_cash_flow = self.amount
            self.transaction_cash_flow_local = self.transaction_cash_flow * self.fx_rate

    def handle_dividend(self: CalculateAggregates) -> None:
        """Handle a dividend payment."""
        if self.pnl_dividend is None:
            self.pnl_dividend = 0.0

        if self.amount:
            self.pnl_dividend += self.amount
            self.transaction_cash_flow = self.amount
            self.transaction_cash_flow_local = self.transaction_cash_flow * self.fx_rate

    def handle_buy(self: CalculateAggregates) -> None:
        """Handle a buy transaction."""
        self.pnl_price = None  # force pnl for price to None
        self.pnl_dividend = None  # force pnl for dividend to None
        self.pnl_interest = None  # force pnl for interest to None

        if self.sum_held is None:
            self.sum_held = 0.0

        if self.cf_ex_commission is None:
            self.cf_ex_commission = 0.0

        if self.cost_basis_delta is None:
            self.cost_basis_delta = 0.0

        if self.sum_cost_basis_delta is None:
            self.sum_cost_basis_delta = 0.0

        if self.no_traded is None or self.nominal_price is None:
            return

        transaction_cash_flow: float = -(self.no_traded * self.nominal_price)
        if self.nominal_commission:
            transaction_cash_flow += self.nominal_commission
        self.transaction_cash_flow = transaction_cash_flow
        self.transaction_cash_flow_local = self.transaction_cash_flow * self.fx_rate

        self.sum_held += self.no_traded
        self.cf_ex_commission = -(self.no_traded * self.nominal_price)
        self.cost_basis_delta = self.cf_ex_commission
        self.sum_cost_basis_delta += self.cost_basis_delta
        self.avg_cost_basis = self.sum_cost_basis_delta / self.sum_held * -1

    def handle_sell(self: CalculateAggregates) -> None:
        """Handle a sell transaction."""
        if (
            self.avg_cost_basis is None
            or self.sum_cost_basis_delta is None
            or self.sum_held is None
            or self.no_traded is None
            or self.nominal_price is None
        ):
            return

        transaction_cash_flow: float = -(self.no_traded * self.nominal_price)
        if self.nominal_commission:
            transaction_cash_flow += self.nominal_commission
        self.transaction_cash_flow = transaction_cash_flow
        self.transaction_cash_flow_local = self.transaction_cash_flow * self.fx_rate

        self.sum_held += self.no_traded
        self.pnl_price = (
            (self.nominal_price - self.avg_cost_basis) * self.no_traded * -1
        )
        self.cost_basis_delta = self.avg_cost_basis * self.no_traded * -1
        self.cf_ex_commission = self.nominal_price * self.no_traded * -1

        # Everything has been sold
        if round(self.sum_held, 0) <= 0:
            self.cost_basis_delta = None
            self.sum_cost_basis_delta = None
            self.avg_cost_basis = None
            self.sum_held = None
        else:
            self.cost_basis_delta = self.avg_cost_basis * self.no_traded * -1
            self.sum_cost_basis_delta += self.cost_basis_delta
            self.avg_cost_basis = self.sum_cost_basis_delta / self.sum_held * -1

    def calculate_total_pnl(self: CalculateAggregates) -> None:
        """Calculate total PnL."""
        pnl: float = 0.0

        if self.pnl_interest:
            pnl += self.pnl_interest

        if self.pnl_commission:
            pnl += self.pnl_commission

        if self.pnl_dividend:
            pnl += self.pnl_dividend

        if self.pnl_price:
            pnl += self.pnl_price

        if pnl == 0.0:
            self.pnl_total = None
            return

        self.pnl_total = pnl

    def set_base_data(self: CalculateAggregates, row: dict[str, Any]) -> None:
        """Set base data from the transaction."""
        self.amount = row[ColumnNameValues.AMOUNT]
        self.broker = row[ColumnNameValues.BROKER]
        self.isin = row[ColumnNameValues.ISIN_CODE]
        self.name = row[ColumnNameValues.NAME]
        self.source = row[ColumnNameValues.SOURCE]
        self.transaction_type = row[ColumnNameValues.TRANSACTION_TYPE]
        self.transaction_date = row[ColumnNameValues.TRANSACTION_DATE]
        self.transaction_year = row[ColumnNameValues.TRANSACTION_YEAR]
        self.nominal_commission = row[ColumnNameValues.COMMISSION]
        self.fx_rate = row[ColumnNameValues.FX]

        if row.get(ColumnNameValues.PRICE):
            self.nominal_price = row[ColumnNameValues.PRICE]
        else:
            self.nominal_price = None

        if row.get(ColumnNameValues.NO_TRADED):
            self.no_traded = row[ColumnNameValues.NO_TRADED]
        else:
            self.no_traded = None

    def add_transaction(self: CalculateAggregates) -> None:
        """Add the transaction back to a data list."""
        self.calculated_transaction_list.append(
            {
                ColumnNameValues.AMOUNT: self.amount,
                ColumnNameValues.AVG_PRICE: self.avg_cost_basis,
                ColumnNameValues.AVG_FX: None,
                ColumnNameValues.BROKER: self.broker,
                ColumnNameValues.CASH_FLOW_LOCAL: self.transaction_cash_flow_local,
                ColumnNameValues.CF_EX_COMMISSION: self.cf_ex_commission,
                ColumnNameValues.COMMISSION: self.nominal_commission,
                ColumnNameValues.COST_BASIS_DELTA: self.cost_basis_delta,
                ColumnNameValues.FX: self.fx_rate,
                ColumnNameValues.ISIN_CODE: self.isin,
                ColumnNameValues.NAME: self.name,
                ColumnNameValues.NO_HELD: self.sum_held,
                ColumnNameValues.NO_TRADED: self.no_traded,
                ColumnNameValues.PRICE: self.nominal_price,
                ColumnNameValues.REALIZED_PNL: self.pnl_total,
                ColumnNameValues.REALIZED_PNL_COMMISSION: self.pnl_commission,
                ColumnNameValues.REALIZED_PNL_EQ: self.pnl_price,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: self.pnl_dividend,
                ColumnNameValues.REALIZED_PNL_INTEREST: self.pnl_interest,
                ColumnNameValues.SOURCE: self.source,
                ColumnNameValues.SUM_COST_BASIS_DELTA: self.sum_cost_basis_delta,
                ColumnNameValues.TRANSACTION_CASH_FLOW: self.transaction_cash_flow,
                ColumnNameValues.TRANSACTION_DATE: self.transaction_date,
                ColumnNameValues.TRANSACTION_YEAR: self.transaction_year,
                ColumnNameValues.TRANSACTION_TYPE: self.transaction_type,
            },
        )
