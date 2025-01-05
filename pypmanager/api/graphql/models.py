"""Models."""

from __future__ import annotations

from strawberry.experimental.pydantic import type as pydantic_type

from pypmanager.helpers.security import Security


@pydantic_type(model=Security, all_fields=True)
class SecurityResponse:
    """Represent a security response."""
