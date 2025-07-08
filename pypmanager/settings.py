"""Settings."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class TypedSettings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug_name: str | None = None

    # Set APP_ROOT and APP_DATA, allowing override via environment variable
    APP_ROOT: Path = Path(
        os.getenv("APP_ROOT", "/workspaces/pypmanager/pypmanager")
    ).resolve()
    APP_DATA: Path = Path(os.getenv("APP_DATA", APP_ROOT / "data")).resolve()

    dir_config: Path = APP_ROOT / "configuration"
    dir_static: Path = APP_ROOT / "../frontend/static"
    dir_templates: Path = APP_ROOT / "../frontend/templates"

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
        return self.APP_DATA

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
