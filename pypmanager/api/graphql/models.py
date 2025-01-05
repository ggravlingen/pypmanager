"""Models."""

from __future__ import annotations

import strawberry
from strawberry.experimental.pydantic import type as pydantic_type

from pypmanager.helpers.security import Security


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
class ResultStatementRow:
    """Represent a row in the result statement."""

    item_name: str
    year_list: list[int]
    amount_list: list[float | None]
    is_total: bool


@pydantic_type(model=Security, all_fields=True)
class SecurityResponse:
    """Represent a security response."""
