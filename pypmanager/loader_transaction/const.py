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
    INTEREST = "interest"
    SELL = "sell"
    TAX = "tax"
    WITHDRAW = "withdraw"


class AccountNameValues(StrEnum):
    """Represent names of accounts."""

    CASH = "cash"
    EQUITY = "equity"
    SECURITIES = "securities"
    IS_COSTS = "income_statement_costs"


class CurrencyValues(StrEnum):
    """Represent names of currencies."""

    SEK = "SEK"


class ColumnNameValues(StrEnum):
    """Represent names of columns in the ledger."""

    ACCOUNT = "ledger_account"
    AMOUNT = "amount"
    CREDIT = "credit"
    DEBIT = "debit"
    NO_TRADED = "no_traded"
    PRICE = "price"
    TRANSACTION_TYPE = "transaction_type"


LOGGER = logging.getLogger(__package__)
