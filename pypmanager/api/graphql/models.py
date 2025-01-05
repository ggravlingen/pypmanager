"""Models."""

from __future__ import annotations

import strawberry
from strawberry.experimental.pydantic import type as pydantic_type

from pypmanager.helpers.security import Security


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
