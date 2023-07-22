"""Settings."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Settings."""

    DEBUG_NAME = os.getenv("DEBUG_NAME")
    DIR_CONFIG = os.path.abspath("config")
    DIR_DATA = os.path.abspath("data")
    DIR_STATIC = os.path.abspath("pypmanager/server/static")
    FILE_MARKET_DATA = os.path.abspath(os.path.join("data", "market_data.csv"))
