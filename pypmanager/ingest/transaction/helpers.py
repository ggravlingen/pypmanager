"""Helper functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from .avanza import AvanzaLoader
from .generic import GenericLoader
from .lysa import LysaLoader

if TYPE_CHECKING:
    from datetime import datetime


def load_transaction_files(
    report_date: datetime | None = None,
    *,
    sort_by_date_descending: bool = False,
) -> pd.DataFrame:
    """Load transaction files and return a sorted DataFrame."""
    df_generic = GenericLoader(report_date).df_final
    df_avanza = AvanzaLoader(report_date).df_final
    df_lysa = LysaLoader(report_date).df_final

    df_combined = pd.concat([df_generic, df_avanza, df_lysa])

    if sort_by_date_descending:
        return df_combined.sort_index(ascending=False)

    return df_combined
