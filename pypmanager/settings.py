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

    @property
    def dir_data(self: TypedSettings) -> Path:
        """Return data directory."""
        if self.is_demo:
            return Path("data-demo").resolve()

        return Path("data").resolve()

    dir_config: Path = Path("pypmanager/configuration").resolve()
    dir_static: Path = Path("frontend/static").resolve()
    dir_templates: Path = Path("frontend/templates").resolve()

    system_time_zone: ZoneInfo = ZoneInfo("Europe/Stockholm")

    @property
    def dir_market_data(self: TypedSettings) -> Path:
        """Return folder path for market data."""
        folder_path = Path(self.dir_data)
        return (folder_path / "market_data").resolve()

    @property
    def dir_transaction_data(self: TypedSettings) -> Path:
        """Return folder path for transaction data."""
        folder_path = Path(self.dir_data)
        return (folder_path / "transactions").resolve()

    @property
    def file_market_data_config(self: TypedSettings) -> Path:
        """Return market data file."""
        folder_path = Path(self.dir_config)
        return (folder_path / "market_data.yaml").resolve()

    is_demo: bool = False


Settings = TypedSettings()
