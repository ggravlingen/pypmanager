"""Helpers."""

from datetime import datetime
import logging
import time
from typing import cast

import pandas as pd

from pypmanager.analytics.holding import Holding
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
from pypmanager.loader_transaction.const import ColumnNameValues

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


async def get_holdings() -> list[Holding]:
    """Return a list of current holdings."""
    df_general_ledger = get_general_ledger()
    all_securities = cast(list[str], df_general_ledger[ColumnNameValues.NAME].unique())

    holdings: list[Holding] = []
    for security_name in all_securities:
        start_time = time.time()

        holding = Holding(
            name=security_name,
            df_general_ledger=df_general_ledger,
        )

        end_time = time.time()

        LOGGER.info(
            f"Calculated {security_name} in {round((end_time - start_time), 4)}s"
        )

        if holding.total_pnl == 0:
            continue

        holdings.append(holding)

    # Order by name
    holdings = sorted(holdings, key=lambda x: x.name)

    return holdings


async def download_market_data() -> None:
    """Load JSON-data from a source."""
    sources = _load_sources()

    for source in sources:
        LOGGER.info(
            f"Parsing {source.isin_code} using "
            f"{source.loader_class.replace('pypmanager.loader_market_data.', '')}"
        )

        try:
            data_loader_klass = _class_importer(source.loader_class)
        except AttributeError as err:
            raise DataError("Unable to load data", err) from err

        try:
            loader = data_loader_klass(
                lookup_key=source.lookup_key,
                isin_code=source.isin_code,
                name=source.name,
            )
            _upsert_df(data=loader.to_source_data(), source_name=loader.source)
        except AttributeError:
            LOGGER.error(f"Unable to load {loader}")
