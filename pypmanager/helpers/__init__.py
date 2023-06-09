"""Helpers."""

from datetime import datetime
import logging
from typing import cast

import pandas as pd

from pypmanager.error import DataError
from pypmanager.loader_market_data.utils import (
    _class_importer,
    _load_sources,
    _upsert_df,
)
from pypmanager.loader_transaction import (
    AvanzaLoader,
    GeneralLedger,
    LysaLoader,
    MiscLoader,
)

LOGGER = logging.getLogger(__package__)


def load_transaction_files(report_date: datetime | None = None) -> pd.DataFrame:
    """Load all transaction files into a Dataframe."""
    return cast(
        pd.DataFrame,
        pd.concat(
            [
                MiscLoader(report_date).df_final,
                AvanzaLoader(report_date).df_final,
                LysaLoader(report_date).df_final,
            ],
        ),
    )


def get_general_ledger(report_date: datetime | None = None) -> pd.DataFrame:
    """Return the general ledger."""
    all_data = load_transaction_files(report_date=report_date)
    return GeneralLedger(transactions=all_data).output_df


async def download_market_data() -> None:
    """Load JSON-data from a source."""
    sources = _load_sources()

    for source in sources:
        LOGGER.info(f"Parsing {source.isin_code} using {source.loader_class}")

        try:
            data_loader_klass = _class_importer(source.loader_class)
        except AttributeError as err:
            raise DataError("Unable to load data", err) from err

        loader = data_loader_klass(
            lookup_key=source.lookup_key,
            isin_code=source.isin_code,
            name=source.name,
        )
        _upsert_df(data=loader.to_source_data(), source_name=loader.source)
