"""Helper functions."""

from __future__ import annotations

import yaml

from pypmanager.helpers.security import (
    SecurityData,
)
from pypmanager.settings import Settings

from .security import AsyncDbSecurity, SecurityModel


async def sync_files_to_db() -> None:
    """Sync the security YAML files to the database."""
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

    data = [
        SecurityModel(
            isin_code=security.isin_code,
            name=security.name,
            currency=security.currency,
        )
        for security in security_data.values()
    ]

    async with AsyncDbSecurity() as db:
        await db.async_store_data(data=data)
