"""Util functions."""
from __future__ import annotations

from datetime import datetime
from typing import cast

import pandas as pd

from .avanza import AvanzaLoader
from .lysa import LysaLoader
from .misc import MiscLoader


def load_data(report_date: datetime | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Load all data."""
    all_data = cast(
        pd.DataFrame,
        pd.concat(
            [
                MiscLoader(report_date).df_final,
                AvanzaLoader(report_date).df_final,
                LysaLoader(report_date).df_final,
            ],
        ),
    )

    all_securities = cast(list[str], all_data.name.unique())

    return (
        all_data,
        all_securities,
    )
