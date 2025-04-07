"""Settings."""

from __future__ import annotations

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

    dir_config: Path = Path("pypmanager/configuration")
    dir_static: Path = Path("frontend/static")
    dir_templates: Path = Path("frontend/templates")

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
        return Path("data")

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
        return self.dir_configuration_local / "database.sqlite"


Settings = TypedSettings()
