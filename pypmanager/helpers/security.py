"""Helper functions for working with securities."""

import logging

from pydantic import BaseModel
from strawberry.experimental.pydantic import type as pydantic_type

from pypmanager.database.security import AsyncDbSecurity

LOGGER = logging.getLogger(__name__)


class SecurityData(BaseModel):
    """Represent a security."""

    name: str
    """The name of the security."""
    isin_code: str
    """The ISIN code of the security."""
    currency: str | None = None
    """The currency of the security's price."""


@pydantic_type(model=SecurityData, all_fields=True)
class SecurityDataResponse:
    """Convert SecurityData to a GraphQL response."""


async def async_security_map_isin_to_security() -> dict[str, SecurityData]:
    """Return a dict to get security information from an ISIN."""
    async with AsyncDbSecurity() as db:
        if db_data := await db.async_filter_all():
            return {
                security.isin_code: SecurityData(
                    name=security.name,
                    isin_code=security.isin_code,
                    currency=security.currency,
                )
                for security in db_data
            }

    return {}


async def async_security_map_name_to_isin() -> dict[str, str]:
    """Return a dict to get the ISIN code from a security name."""
    security_data = await async_security_map_isin_to_security()
    return {security.name: isin for isin, security in security_data.items()}
