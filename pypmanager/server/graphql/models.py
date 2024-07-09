"""Models."""

from __future__ import annotations

from datetime import date  # noqa: TCH003

import strawberry


@strawberry.type
class LedgerRow:
    """Represent a row in the general ledger."""

    report_date: date
    broker: str
    source: str
