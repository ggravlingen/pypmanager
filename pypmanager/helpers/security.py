"""Helper functions for working with securities."""

import logging

from pydantic import BaseModel
from strawberry.experimental.pydantic import type as pydantic_type
import yaml

from pypmanager.settings import Settings

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
    """Asynchronously load security data from a YAML file."""
    with Settings.security_config.open(encoding="UTF-8") as file:
        yaml_data = yaml.safe_load(file)

        security_data = {item["isin_code"]: SecurityData(**item) for item in yaml_data}

    if Settings.security_config_local and Settings.security_config_local.exists():
        with Settings.security_config_local.open(encoding="UTF-8") as file:
            yaml_data = yaml.safe_load(file)

            # Append security_data with local security data
            security_data.update(
                {item["isin_code"]: SecurityData(**item) for item in yaml_data}
            )

    return security_data
