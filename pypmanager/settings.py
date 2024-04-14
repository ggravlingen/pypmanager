"""Settings."""

from __future__ import annotations

import os

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

    dir_config: str = os.path.abspath("config")

    @property
    def dir_data(self: TypedSettings) -> str:
        """Return data directory."""
        if self.is_demo:
            return os.path.abspath("data-demo")

        return os.path.abspath("data")

    dir_static: str = os.path.abspath("pypmanager/server/static")

    @property
    def file_market_data(self: TypedSettings) -> str:
        """Return market data file."""
        return os.path.abspath(os.path.join(self.dir_data, "market_data.csv"))

    @property
    def file_market_data_config(self: TypedSettings) -> str:
        """Return market data file."""
        return os.path.abspath(os.path.join(self.dir_config, "market_data.yaml"))

    is_demo: bool = False


Settings = TypedSettings()
