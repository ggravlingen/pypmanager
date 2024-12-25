"""Models."""

from __future__ import annotations

from datetime import date  # noqa: TC003

import strawberry
from strawberry.experimental.pydantic import type as pydantic_type

from pypmanager.helpers.security import Security


@strawberry.type
class BaseTransactionRow:
    """Represent a base transaction row."""

    transaction_date: date
    broker: str
    source: str
    action: str
    name: str | None
    no_traded: float | None
    commission: float | None
    fx: float | None


@strawberry.type
class TransactionRow(BaseTransactionRow):
    """Represent a transaction row."""

    isin_code: str | None
    price: float | None
    currency: str | None
    cash_flow: float | None
    cost_base_average: float | None
    pnl_total: float | None
    pnl_trade: float | None
    pnl_dividend: float | None
    quantity_held: float | None


@strawberry.type
class LedgerRow(BaseTransactionRow):
    """Represent a row in the general ledger."""

    agg_buy_volume: float | None
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


@strawberry.type
class ResultStatementRow:
    """Represent a row in the result statement."""

    item_name: str
    year_list: list[int]
    amount_list: list[float | None]
    is_total: bool


@pydantic_type(model=Security, all_fields=True)
class SecurityResponse:
    """Represent a security response."""
