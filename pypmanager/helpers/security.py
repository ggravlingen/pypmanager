"""Helper functions for working with securities."""

import logging

from pydantic import BaseModel
import yaml

from pypmanager.settings import Settings

LOGGER = logging.getLogger(__name__)


class Security(BaseModel):
    """Represent a security."""

    name: str
    """The name of the security."""
    isin_code: str
    """The ISIN code of the security."""
    currency: str | None = None
    """The currency of the security's price."""


async def async_load_security_data() -> dict[str, Security]:
    """Asynchronously load security data from a YAML file."""
    with Settings.security_config.open(encoding="UTF-8") as file:
        yaml_data = yaml.safe_load(file)

        security_data = {item["isin_code"]: Security(**item) for item in yaml_data}

    if Settings.security_config_local and Settings.security_config_local.exists():
        with Settings.security_config_local.open(encoding="UTF-8") as file:
            yaml_data = yaml.safe_load(file)

            # Append security_data with local security data
            security_data.update(
                {item["isin_code"]: Security(**item) for item in yaml_data}
            )

    return security_data
