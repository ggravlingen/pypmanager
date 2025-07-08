"""Settings."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


ROOT_FOLDER = Path(os.getenv("PYP_APP_ROOT", Path.cwd())).resolve()
"""E.g. /app."""
APP_ROOT = ROOT_FOLDER / "pypmanager"
"""E.g. /app/pypmanager."""
APP_DATA = Path(os.getenv("PYP_APP_DATA", ROOT_FOLDER / "data")).resolve()
"""E.g. /app/data."""
APP_FRONTEND = ROOT_FOLDER / "frontend"
"""E.g. /app/frontend."""


class TypedSettings(BaseSettings):
    """Settings."""

    dir_config: Path = APP_ROOT / "configuration"
    dir_static: Path = APP_FRONTEND / "static"
    dir_templates: Path = APP_FRONTEND / "templates"

    system_time_zone: ZoneInfo = ZoneInfo("Europe/Stockholm")

    @property
    def file_market_data_config(self: TypedSettings) -> Path:
        """Return market data file."""
        return self.dir_config / "market_data.yaml"

    @property
    def security_config(self: TypedSettings) -> Path:
        """Return security configuration file."""
        return self.dir_config / "security.yaml"

    @property
    def dir_data_local(self: TypedSettings) -> Path:
        """Return data directory."""
        return APP_DATA

    @property
    def dir_configuration_local(self: TypedSettings) -> Path:
        """Return local configuration path."""
        return self.dir_data_local / "configuration"

    @property
    def dir_market_data_local(self: TypedSettings) -> Path:
        """Return folder path for market data."""
        return self.dir_data_local / "market_data"

    @property
    def dir_transaction_data_local(self: TypedSettings) -> Path:
        """Return folder path for transaction data."""
        return self.dir_data_local / "transactions"

    @property
    def file_market_data_config_local(self: TypedSettings) -> Path | None:
        """Return local market data file."""
        local_market_data = self.dir_configuration_local / "market_data.yaml"
        if local_market_data.exists():
            return local_market_data

        return None

    @property
    def security_config_local(self: TypedSettings) -> Path | None:
        """Return local security configuration file."""
        local_market_data = self.dir_configuration_local / "security.yaml"
        if local_market_data.exists():
            return local_market_data

        return None

    @property
    def database_local(self: TypedSettings) -> Path:
        """Return path to local SQL lite database."""
        return self.dir_data_local / "database" / "database.sqlite"


Settings = TypedSettings()

logging.basicConfig(level=logging.INFO)

for _module in ("aiosqlite",):
    logging.getLogger(_module).setLevel(logging.INFO)
