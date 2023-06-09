"""Aggregation calculator."""
from datetime import date
import logging
from typing import Any

import pandas as pd

from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues

LOGGER = logging.Logger(__name__)


class CalculateAggregates:
    """Class to calculate aggregates for a security."""

    input_data: list[dict[str, Any]]
    calculated_transaction_list: list[dict[str, Any]] = []
    output_data: pd.DataFrame

    # The transaction's amount
    amount: float | None
    # Name of the broker
    broker: str
    # Name of the source
    source: str
    # The date of the transaction
    transaction_date: date
    # Type of transaction, eg buy/sell
    transaction_type: str
    # Currency of the transaction
    nominal_ccy: str
    # Number of securities traded in the transaction
    no_traded: int
    # The name of the security
    name: str
    # The price of the security
    nominal_price: float
    # The commission paid. None if there is no commission.
    nominal_commission: float | None
    # Cumulative sum of bought/sold. None if all are sold.
    cf_ex_commission: float | None
    # no_traded x nominal_price
    nominal_cf: float
    # The current amount held
    sum_held: float | None
    # The total PnL
    pnl_total: float | None
    # The PnL from changes in the security price
    pnl_price: float | None
    # The PnL from commissions paid
    pnl_commission: float | None
    # The PnL from interest paid or received
    pnl_interest: float = 0.0
    # The PnL from dividends received
    pnl_dividend: float = 0.0
    # The delta on the cost bases from this transaction
    cost_basis_delta: float | None
    # The cumulative sum of cost_basis_delta
    sum_cost_basis_delta: float | None
    # The average cost for the currently held securities
    avg_cost_basis: float | None

    def __init__(self, security_transactions: pd.DataFrame) -> None:
        """Init class."""
        data_copy = security_transactions.copy()
        self.data = data_copy

        data_copy[
            ColumnNameValues.TRANSACTION_DATE
        ] = data_copy.index  # Convert index to a column

        self.input_data = data_copy.to_dict("records", index=True)

        self.parse_transactions()

        final_df = pd.DataFrame(self.calculated_transaction_list)
        final_df = final_df.set_index(ColumnNameValues.TRANSACTION_DATE)
        self.output_data = final_df

    def parse_transactions(self) -> None:
        """Loop through all transactions."""
        for row in self.input_data:
            self.set_base_data(row=row)

            if self.transaction_type == TransactionTypeValues.INTEREST.value:
                self.handle_interest()

            if self.transaction_type == TransactionTypeValues.DIVIDEND.value:
                self.handle_dividend()

        self.calculate_total_pnl()
        self.add_transaction()

    def handle_interest(self) -> None:
        """Handle an interest payment."""
        if self.amount:
            self.pnl_interest += self.amount

    def handle_dividend(self) -> None:
        """Handle an interest payment."""
        if self.amount:
            self.pnl_dividend += self.amount

    def calculate_total_pnl(self) -> None:
        """Calculate total PnL."""
        pnl = 0.0
        if self.pnl_interest:
            pnl += self.pnl_interest

        if self.pnl_dividend:
            pnl += self.pnl_dividend

        self.pnl_total = pnl

    def set_base_data(self, row: dict[str, Any]) -> None:
        """Set base data from the transaction."""
        self.amount = row[ColumnNameValues.AMOUNT]
        self.broker = row[ColumnNameValues.BROKER]
        self.name = row[ColumnNameValues.NAME]
        self.source = row[ColumnNameValues.SOURCE]
        self.transaction_type = row[ColumnNameValues.TRANSACTION_TYPE]
        self.transaction_date = row[ColumnNameValues.TRANSACTION_DATE]

    def add_transaction(self) -> None:
        """Add the transaction back to a data list."""
        self.calculated_transaction_list.append(
            {
                ColumnNameValues.AMOUNT: self.amount,
                ColumnNameValues.BROKER: self.broker,
                ColumnNameValues.NAME: self.name,
                ColumnNameValues.REALIZED_PNL: self.pnl_total,
                ColumnNameValues.REALIZED_PNL_DIVIDEND: self.pnl_dividend,
                ColumnNameValues.REALIZED_PNL_INTEREST: self.pnl_interest,
                ColumnNameValues.SOURCE: self.source,
                ColumnNameValues.TRANSACTION_DATE: self.transaction_date,
                ColumnNameValues.TRANSACTION_TYPE: self.transaction_type,
            }
        )
