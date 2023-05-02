"""Settings."""
from __future__ import annotations

import os


class Settings:
    """Settings."""

    DIR_DATA = os.path.abspath("data")
    FILE_MARKET_DATA = os.path.abspath(os.path.join("data", "market_data.csv"))
