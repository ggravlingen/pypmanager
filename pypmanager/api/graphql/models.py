"""Models."""

from __future__ import annotations

from datetime import date  # noqa: TCH003

import strawberry


@strawberry.type
class BaseTransactionRow:
    """Represent a base transaction row."""

    transaction_date: date
    broker: str
    source: str
    action: str
    name: str
    no_traded: float | None
    commission: float | None
    fx: float | None


@strawberry.type
class TransactionRow(BaseTransactionRow):
    """Represent a transaction row."""

    price: float | None


@strawberry.type
class LedgerRow(BaseTransactionRow):
    """Represent a row in the general ledger."""

    agg_buy_volume: float | None
    average_price: float | None
    amount: float | None
    cash_flow: float | None
    average_fx_rate: float | None
    account: str
    credit: float | None
    debit: float | None


@strawberry.type
class PortfolioContentRow:
    """Represent a row in the current portfolio content."""

    name: str
    date_market_value: str | None
    invested_amount: float | None
    market_value: float | None
    current_holdings: float | None
    current_price: float | None
    average_price: float | None
    return_pct: float | None
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float


@strawberry.type
class HistoricalPortfolioRow:
    """Represent a row in the historical portfolio content."""

    report_date: date
    invested_amount: float | None
    market_value: float | None
    return_pct: float | None
    realized_pnl: float | None
    unrealized_pnl: float | None
