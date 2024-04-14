"""Models."""

from __future__ import annotations

from typing import TYPE_CHECKING

import strawberry

if TYPE_CHECKING:
    from datetime import date


@strawberry.type
class LedgerRow:
    """Represent a row in the general ledger."""

    date: date
    broker: str
    source: str
