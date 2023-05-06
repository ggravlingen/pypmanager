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
    df_a = AvanzaLoader(report_date).df
    df_b = LysaLoader(report_date).df
    df_c = MiscLoader(report_date).df

    all_data = cast(pd.DataFrame, pd.concat([df_a, df_b, df_c]))

    all_securities = cast(list[str], all_data.name.unique())

    return (
        all_data,
        all_securities,
    )
