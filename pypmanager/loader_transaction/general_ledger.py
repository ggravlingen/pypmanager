"""Class to create a general ledger."""
from __future__ import annotations

from typing import Any

import pandas as pd

from .calculate_aggregates import calculate_results
from .const import AccountNameValues, ColumnNameValues, TransactionTypeValues

MAP_PNL_ACCOUNT = {
    TransactionTypeValues.SELL: AccountNameValues.IS_PNL,
    TransactionTypeValues.FEE: AccountNameValues.IS_FEE,
    TransactionTypeValues.FEE_CREDIT: AccountNameValues.IS_FEE,
    TransactionTypeValues.TAX: AccountNameValues.IS_TAX,
    TransactionTypeValues.DIVIDEND: AccountNameValues.IS_DIVIDEND,
    TransactionTypeValues.CASHBACK: AccountNameValues.IS_CASHBACK,
    TransactionTypeValues.INTEREST: AccountNameValues.IS_INTEREST,
}

RowType = dict[str, Any]
ListType = list[RowType]


class TransactionMacro:
    """Macros run depending on transactions."""

    profit_loss: float
    profit_loss_eq: float
    profit_loss_fx: float | None

    def __init__(self, row: RowType) -> None:
        """Init class."""
        self.row = row

        self.amount = row[ColumnNameValues.AMOUNT]
        self.amount_local = row[ColumnNameValues.CASH_FLOW_LOCAL]
        self.transaction_type = row[ColumnNameValues.TRANSACTION_TYPE]
        self.profit_loss = row[ColumnNameValues.REALIZED_PNL]
        self.profit_loss_eq = row[ColumnNameValues.REALIZED_PNL_EQ]
        self.profit_loss_fx = None

        if row[ColumnNameValues.AVG_PRICE] and row[ColumnNameValues.NO_TRADED]:
            self.invested_amount = (
                row[ColumnNameValues.AVG_PRICE] * row[ColumnNameValues.NO_TRADED]
            )

        self.credit_rows: ListType = []
        self.debit_rows: ListType = []

    def buy(self) -> TransactionMacro:
        """Record buy transactions."""
        credit_row = self.row.copy()
        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        # Amount is negative in the row data due to being a cash outflow
        credit_row[ColumnNameValues.CREDIT] = -self.amount_local
        credit_row[ColumnNameValues.REALIZED_PNL_EQ] = None
        credit_row[ColumnNameValues.REALIZED_PNL_FX] = None

        debit_row = self.row.copy()
        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.SECURITIES
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.AVG_PRICE] = None
        debit_row[ColumnNameValues.COMMISSION] = None
        # Amount is negative in the row data due to being a cash outflow
        debit_row[ColumnNameValues.DEBIT] = -self.amount
        debit_row[ColumnNameValues.NO_TRADED] = None
        debit_row[ColumnNameValues.NO_HELD] = None
        debit_row[ColumnNameValues.REALIZED_PNL] = None
        debit_row[ColumnNameValues.REALIZED_PNL_EQ] = None
        debit_row[ColumnNameValues.REALIZED_PNL_FX] = None
        debit_row[ColumnNameValues.PRICE] = None
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

        self.credit_rows.append(credit_row)
        self.debit_rows.append(debit_row)

        return self

    def deposit(self) -> TransactionMacro:
        """Record a deposit."""
        credit_row = self.row.copy()

        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
        credit_row[ColumnNameValues.CREDIT] = self.amount

        debit_row = self.row.copy()
        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.COMMISSION] = None
        debit_row[ColumnNameValues.DEBIT] = self.amount
        debit_row[ColumnNameValues.NO_TRADED] = None
        debit_row[ColumnNameValues.REALIZED_PNL] = None
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

        self.credit_rows.append(credit_row)
        self.debit_rows.append(debit_row)

        return self

    def dividend(self) -> TransactionMacro:
        """Record a dividend."""
        credit_row = self.row.copy()

        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
        credit_row[ColumnNameValues.CREDIT] = self.amount
        credit_row[ColumnNameValues.NO_TRADED] = None
        credit_row[ColumnNameValues.REALIZED_PNL] = None

        debit_row = self.row.copy()
        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.COMMISSION] = None
        debit_row[ColumnNameValues.DEBIT] = self.amount
        debit_row[ColumnNameValues.NO_TRADED] = None
        debit_row[ColumnNameValues.REALIZED_PNL] = self.amount
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

        self.credit_rows.append(credit_row)
        self.debit_rows.append(debit_row)

        return self

    def fee_tax(self) -> TransactionMacro:
        """Record a fee or tax cost."""
        credit_row = self.row.copy()

        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        credit_row[ColumnNameValues.CREDIT] = -self.amount

        debit_row = self.row.copy()
        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.COMMISSION] = None
        debit_row[ColumnNameValues.DEBIT] = -self.amount
        debit_row[ColumnNameValues.NO_TRADED] = None
        debit_row[ColumnNameValues.REALIZED_PNL] = None
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

        self.credit_rows.append(credit_row)
        self.debit_rows.append(debit_row)

        return self

    def fee_credit(self) -> TransactionMacro:
        """Record a fee or tax cost."""
        credit_row = self.row.copy()

        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
        credit_row[ColumnNameValues.CREDIT] = self.amount

        debit_row = self.row.copy()
        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        debit_row[ColumnNameValues.AMOUNT] = None
        debit_row[ColumnNameValues.COMMISSION] = None
        debit_row[ColumnNameValues.DEBIT] = self.amount
        debit_row[ColumnNameValues.NO_TRADED] = None
        debit_row[ColumnNameValues.REALIZED_PNL] = None
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

        self.credit_rows.append(credit_row)
        self.debit_rows.append(debit_row)

        return self

    def pnl_equity(self) -> TransactionMacro:  # noqa: PLR0915
        """Book profit/loss against equity."""
        credit_row = self.row.copy()
        credit_row_2 = self.row.copy()
        debit_row = self.row.copy()
        debit_row_2 = self.row.copy()

        if not self.profit_loss:
            return self

        if self.profit_loss > 0:
            credit_row[ColumnNameValues.ACCOUNT] = MAP_PNL_ACCOUNT[
                self.transaction_type
            ]
            credit_row[ColumnNameValues.AMOUNT] = None
            credit_row[ColumnNameValues.AVG_PRICE] = None
            credit_row[ColumnNameValues.COMMISSION] = None
            credit_row[ColumnNameValues.CREDIT] = self.profit_loss
            credit_row[ColumnNameValues.PRICE] = None
            credit_row[ColumnNameValues.REALIZED_PNL] = None
            credit_row[ColumnNameValues.REALIZED_PNL_EQ] = None
            credit_row[ColumnNameValues.REALIZED_PNL_FX] = None
            credit_row[ColumnNameValues.NO_TRADED] = None
            credit_row[ColumnNameValues.NO_HELD] = None
            credit_row[ColumnNameValues.TRANSACTION_TYPE] = None
            self.credit_rows.append(credit_row)

            if self.transaction_type == TransactionTypeValues.SELL:
                credit_row_2[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
                credit_row_2[ColumnNameValues.AVG_PRICE] = None
                credit_row_2[ColumnNameValues.AMOUNT] = None
                credit_row_2[ColumnNameValues.COMMISSION] = None
                credit_row_2[ColumnNameValues.CREDIT] = self.profit_loss
                credit_row_2[ColumnNameValues.PRICE] = None
                credit_row_2[ColumnNameValues.REALIZED_PNL] = None
                credit_row_2[ColumnNameValues.REALIZED_PNL_EQ] = None
                credit_row_2[ColumnNameValues.REALIZED_PNL_FX] = None
                credit_row_2[ColumnNameValues.NO_TRADED] = None
                credit_row_2[ColumnNameValues.NO_HELD] = None
                credit_row_2[ColumnNameValues.TRANSACTION_TYPE] = None
                self.credit_rows.append(credit_row_2)

        else:
            debit_row[ColumnNameValues.ACCOUNT] = MAP_PNL_ACCOUNT[self.transaction_type]
            debit_row[ColumnNameValues.AMOUNT] = None
            debit_row[ColumnNameValues.AVG_PRICE] = None
            debit_row[ColumnNameValues.COMMISSION] = None
            debit_row[ColumnNameValues.DEBIT] = -self.profit_loss
            debit_row[ColumnNameValues.NO_TRADED] = None
            debit_row[ColumnNameValues.PRICE] = None
            debit_row[ColumnNameValues.REALIZED_PNL] = None
            debit_row[ColumnNameValues.REALIZED_PNL_EQ] = None
            debit_row[ColumnNameValues.REALIZED_PNL_FX] = None
            debit_row[ColumnNameValues.TRANSACTION_TYPE] = None
            self.debit_rows.append(debit_row)

            if self.transaction_type == TransactionTypeValues.SELL:
                debit_row_2[ColumnNameValues.ACCOUNT] = AccountNameValues.EQUITY
                debit_row_2[ColumnNameValues.AMOUNT] = None
                debit_row_2[ColumnNameValues.AVG_PRICE] = None
                debit_row_2[ColumnNameValues.COMMISSION] = None
                debit_row_2[ColumnNameValues.DEBIT] = -self.profit_loss
                debit_row_2[ColumnNameValues.PRICE] = None
                debit_row_2[ColumnNameValues.REALIZED_PNL] = None
                debit_row_2[ColumnNameValues.REALIZED_PNL_EQ] = None
                debit_row_2[ColumnNameValues.REALIZED_PNL_FX] = None
                debit_row_2[ColumnNameValues.NO_TRADED] = None
                debit_row_2[ColumnNameValues.TRANSACTION_TYPE] = None
                self.debit_rows.append(debit_row_2)

        return self

    def sell(self) -> TransactionMacro:
        """Book a sell."""
        credit_row = self.row.copy()
        debit_row = self.row.copy()

        # We want to reduce the securities account by the nominal invested amount
        # as we haven't marked the AccountNameValues.SECURITIES to market
        credit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.SECURITIES
        credit_row[ColumnNameValues.CREDIT] = self.amount
        credit_row[ColumnNameValues.NO_TRADED] = None
        credit_row[ColumnNameValues.REALIZED_PNL] = None
        credit_row[ColumnNameValues.REALIZED_PNL_EQ] = None
        credit_row[ColumnNameValues.PRICE] = None
        credit_row[ColumnNameValues.AMOUNT] = None

        # The cash amount should be increased by the full amount of the sale
        debit_row[ColumnNameValues.ACCOUNT] = AccountNameValues.CASH
        debit_row[ColumnNameValues.COMMISSION] = None
        debit_row[ColumnNameValues.DEBIT] = self.amount_local
        debit_row[ColumnNameValues.NO_HELD] = None
        debit_row[ColumnNameValues.REALIZED_PNL] = self.profit_loss
        debit_row[ColumnNameValues.REALIZED_PNL_EQ] = self.profit_loss_eq
        debit_row[ColumnNameValues.REALIZED_PNL_FX] = None
        debit_row[ColumnNameValues.TRANSACTION_TYPE] = None

        self.credit_rows.append(credit_row)
        self.debit_rows.append(debit_row)

        return self


def _amend_row(row: RowType) -> ListType:
    """Amend row."""
    row[ColumnNameValues.TRANSACTION_TYPE_INTERNAL] = row[
        ColumnNameValues.TRANSACTION_TYPE
    ]  # A library internal field that can be used for debug filtering

    ledger_list: ListType = []

    transaction_type = row[ColumnNameValues.TRANSACTION_TYPE]
    if transaction_type == TransactionTypeValues.BUY:
        transaction = TransactionMacro(row=row)
        transaction.buy()

    if transaction_type == TransactionTypeValues.DEPOSIT:
        transaction = TransactionMacro(row=row)
        transaction.deposit()

    if transaction_type in [
        TransactionTypeValues.FEE,
        TransactionTypeValues.TAX,
    ]:
        transaction = TransactionMacro(row=row)
        transaction.fee_tax().pnl_equity()

    if transaction_type == TransactionTypeValues.SELL:
        transaction = TransactionMacro(row=row)
        transaction.sell().pnl_equity()

    if transaction_type == TransactionTypeValues.FEE_CREDIT:
        transaction = TransactionMacro(row=row)
        transaction.fee_credit().pnl_equity()

    if transaction_type == TransactionTypeValues.DIVIDEND:
        transaction = TransactionMacro(row=row)
        transaction.dividend().pnl_equity()

    if transaction_type == TransactionTypeValues.INTEREST:
        transaction = TransactionMacro(row=row)
        transaction.deposit().pnl_equity()

    if transaction_type == TransactionTypeValues.CASHBACK:
        transaction = TransactionMacro(row=row)
        transaction.deposit().pnl_equity()

    ledger_list.extend(transaction.credit_rows)
    ledger_list.extend(transaction.debit_rows)

    return ledger_list


class GeneralLedger:
    """General ledger."""

    ledger_list: list[dict[str, Any]]
    ledger_df: pd.DataFrame
    output_df: pd.DataFrame

    def __init__(self, transactions: pd.DataFrame) -> None:
        """Init."""
        self.transactions = calculate_results(transactions)

        self.transactions_to_dict()
        self.create_ledger()
        self.set_date_index()

    def transactions_to_dict(self) -> None:
        """Convert transactions to dict."""
        self.ledger_list = self.transactions.reset_index().to_dict(orient="records")

    def create_ledger(self) -> None:
        """Create ledger."""
        ledger_list: list[dict[str, Any]] = []
        for row in self.ledger_list:
            ledger_list.extend(_amend_row(row=row))

        self.output_df = pd.DataFrame(ledger_list)

    def set_date_index(self) -> None:
        """Set index to date."""
        df_tmp = self.output_df.copy()
        # Convert index to a date of format YYYY-MM-DD
        df_tmp[ColumnNameValues.TRANSACTION_DATE] = (
            df_tmp[ColumnNameValues.TRANSACTION_DATE].astype(str).str[:10]
        )
        df_tmp[ColumnNameValues.TRANSACTION_DATE] = pd.to_datetime(
            df_tmp[ColumnNameValues.TRANSACTION_DATE], format="%Y-%m-%d"
        )
        df_tmp = df_tmp.set_index(ColumnNameValues.TRANSACTION_DATE)
        df_tmp.index = df_tmp.index.date

        # Sort by transaction date
        df_tmp = df_tmp.rename_axis(ColumnNameValues.TRANSACTION_DATE).sort_values(
            by=[
                ColumnNameValues.TRANSACTION_DATE,
                ColumnNameValues.TRANSACTION_TYPE_INTERNAL,
            ],
            ascending=[True, True],
        )

        self.output_df = df_tmp
