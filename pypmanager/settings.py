"""Settings."""

from __future__ import annotations

from pathlib import Path

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

    dir_config: Path = Path("config").resolve()

    @property
    def dir_data(self: TypedSettings) -> Path:
        """Return data directory."""
        if self.is_demo:
            return Path("data-demo").resolve()

        return Path("data").resolve()

    dir_static: Path = Path("frontend/static").resolve()
    dir_templates: Path = Path("frontend/templates").resolve()

    @property
    def dir_market_data(self: TypedSettings) -> Path:
        """Return market data file."""
        folder_path = Path(self.dir_data)
        return (folder_path / "market_data").resolve()

    @property
    def file_market_data_config(self: TypedSettings) -> Path:
        """Return market data file."""
        folder_path = Path(self.dir_config)
        return (folder_path / "market_data.yaml").resolve()

    is_demo: bool = False


Settings = TypedSettings()
