"""Models."""

from __future__ import annotations

from datetime import date

import strawberry


@strawberry.type
class LedgerRow:
    """Represent a row in the general ledger."""

    date: date
    broker: str
    source: str
