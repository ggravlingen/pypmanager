"""Models."""

from __future__ import annotations

from datetime import date  # noqa: TCH003

import strawberry


@strawberry.type
class LedgerRow:
    """Represent a row in the general ledger."""

    transaction_date: date
    broker: str
    source: str
    action: str
    name: str
    no_traded: float | None
    agg_buy_volume: float | None
    average_price: float | None
    amount: float | None
    commission: float | None
    cash_flow: float | None
    fx: float | None
    average_fx_rate: float | None
    account: str
    credit: float | None
    debit: float | None
