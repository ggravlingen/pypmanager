"""Helper functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pandas as pd

from .avanza import AvanzaLoader
from .generic import GenericLoader
from .lysa import LysaLoader

if TYPE_CHECKING:
    from datetime import datetime


def load_transaction_files(report_date: datetime | None = None) -> pd.DataFrame:
    """Load all transaction files into a Dataframe."""
    return cast(
        pd.DataFrame,
        pd.concat(
            [
                GenericLoader(report_date).df_final,
                AvanzaLoader(report_date).df_final,
                LysaLoader(report_date).df_final,
            ],
        ),
    )
