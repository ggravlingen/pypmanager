"""Util functions."""
from __future__ import annotations

from datetime import datetime
from typing import cast

import pandas as pd

from .avanza import AvanzaLoader
from .general_ledger import GeneralLedger
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

    calculated_df = GeneralLedger(transactions=all_data).output_df

    all_securities = cast(list[str], calculated_df.name.unique())

    return (
        calculated_df,
        all_securities,
    )
