"""Constants."""
from __future__ import annotations

from enum import StrEnum
import logging

DTYPES_MAP: dict[str, type[str] | type[float]] = {
    "account": str,
    "transaction_type": str,
    "name": str,
    "no_traded": float,
    "price": float,
    "amount": float,
    "commission": float,
    "currency": str,
    "isin_code": str,
}

NUMBER_COLS = [
    "no_traded",
    "price",
    "amount",
    "commission",
    "pnl",
]


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
    AMOUNT = "amount"
    BROKER = "broker"
    COMMISSION = "commission"
    CURRENCY = "currency"
    CREDIT = "credit"
    DEBIT = "debit"
    ISIN_CODE = "isin_code"
    NAME = "name"
    NO_TRADED = "no_traded"
    PRICE = "price"
    REALIZED_PNL = "realized_pnl"
    SOURCE = "source"
    TRANSACTION_DATE = "transaction_date"
    TRANSACTION_TYPE = "transaction_type"
    TRANSACTION_TYPE_INTERNAL = "transaction_type_internal"


class CSVSeparator(StrEnum):
    """Represent CSV-file separators."""

    COMMA = ","
    SEMI_COLON = ";"


LOGGER = logging.getLogger(__package__)
