"""Settings."""
from __future__ import annotations

import os


class Settings:
    """Settings."""

    DIR_CONFIG = os.path.abspath("config")
    DIR_DATA = os.path.abspath("data")
    DIR_STATIC = os.path.abspath("pypmanager/server/static")
    FILE_MARKET_DATA = os.path.abspath(os.path.join("data", "market_data.csv"))
