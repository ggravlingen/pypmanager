"""Constants."""
from __future__ import annotations

from enum import StrEnum

DTYPES_MAP: dict[str, str | float] = {
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
    SELL = "sell"
    INTEREST = "interest"
    TAX = "tax"
    DIVIDEND = "dividend"
