"""Constants."""

from __future__ import annotations

from enum import StrEnum
import logging


class TransactionTypeValues(StrEnum):
    """Represent transaction types."""

    BUY = "buy"
    CASHBACK = "cashback"
    DEPOSIT = "deposit"
    DIVIDEND = "dividend"
    FEE = "fee"
    FEE_CREDIT = "fee_credit"
    INTEREST = "interest"
    SELL = "sell"
    TAX = "tax"
    WITHDRAW = "withdraw"


class AccountNameValues(StrEnum):
    """Represent names of accounts."""

    CASH = "cash"
    EQUITY = "equity"
    SECURITIES = "securities"
    IS_PNL = "is_trading"
    IS_CASHBACK = "is_cashback"
    IS_DIVIDEND = "is_dividends"
    IS_INTEREST = "is_interest"
    IS_FEE = "is_costs_fee"
    IS_TAX = "is_costs_tax"


class CurrencyValues(StrEnum):
    """Represent names of currencies."""

    SEK = "SEK"


class ColumnNameValues(StrEnum):
    """Represent names of columns in the ledger."""

    ACCOUNT = "ledger_account"
    AVG_PRICE = "average_price"
    AVG_FX = "average_fx_rate"
    AMOUNT = "amount"
    BROKER = "broker"
    COMMISSION = "commission"
    CASH_FLOW_LOCAL = "cash_flow_base_ccy"
    CURRENCY = "currency"
    CREDIT = "credit"
    DEBIT = "debit"
    FX = "fx_rate"
    ISIN_CODE = "isin_code"
    NAME = "name"
    NO_TRADED = "no_traded"
    NO_HELD = "cumulative_buy_volume"
    PRICE = "price"
    REALIZED_PNL = "realized_pnl"
    REALIZED_PNL_EQ = "realized_pnl_equity"
    REALIZED_PNL_COMMISSION = "realized_pnl_commission"
    REALIZED_PNL_FX = "realized_pnl_fx"
    REALIZED_PNL_INTEREST = "realized_pnl_interest"
    REALIZED_PNL_DIVIDEND = "realized_pnl_dividend"
    SOURCE = "source"
    TRANSACTION_DATE = "transaction_date"
    TRANSACTION_TYPE = "transaction_type"
    TRANSACTION_TYPE_INTERNAL = "transaction_type_internal"
    CF_EX_COMMISSION = "cf_ex_commission"
    COST_BASIS_DELTA = "cost_basis_delta"
    SUM_COST_BASIS_DELTA = "sum_cost_basis_delta"
    TRANSACTION_CASH_FLOW = "transaction_cash_flow"


class CSVSeparator(StrEnum):
    """Represent CSV-file separators."""

    COMMA = ","
    SEMI_COLON = ";"


NUMBER_COLS = [
    ColumnNameValues.AMOUNT,
    ColumnNameValues.COMMISSION,
    ColumnNameValues.FX,
    ColumnNameValues.NO_TRADED,
    ColumnNameValues.PRICE,
    ColumnNameValues.REALIZED_PNL,
]


LOGGER = logging.getLogger(__package__)
