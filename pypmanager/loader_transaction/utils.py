"""Util functions."""
from __future__ import annotations

from datetime import datetime
from typing import cast

import pandas as pd

from .avanza import AvanzaLoader
from .general_ledger import GeneralLedger
from .lysa import LysaLoader
from .misc import MiscLoader


def get_general_ledger(report_date: datetime | None = None) -> pd.DataFrame:
    """Return the general ledger."""
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

    return GeneralLedger(transactions=all_data).output_df


def load_data(report_date: datetime | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Load all data."""
    df_general_ledger = get_general_ledger(report_date=report_date)

    all_securities = cast(list[str], df_general_ledger.name.unique())

    return (
        df_general_ledger,
        all_securities,
    )
