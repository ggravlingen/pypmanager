"""Helper functions for market data."""

from __future__ import annotations

from asyncio import sleep
from dataclasses import dataclass
from datetime import UTC, date, datetime
from importlib import import_module
import logging
from random import randint
from typing import TYPE_CHECKING, cast

import pandas as pd
from requests import HTTPError
from sqlalchemy.exc import IntegrityError
import strawberry
import yaml

from pypmanager.database.market_data import AsyncMarketDataDB, MarketDataModel
from pypmanager.error import DataError
from pypmanager.helpers.security import async_security_map_isin_to_security
from pypmanager.ingest.market_data.models import Source, Sources
from pypmanager.settings import Settings

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pypmanager.ingest.market_data.base_loader import BaseMarketDataLoader


async def async_sync_csv_to_db() -> None:
    """Sync CSV data to database.

    This function reads market data from CSV files and stores it in the market data
    database.
    """
    all_data: list[MarketDataModel] = []

    for file in Settings.dir_market_data_local.glob("*.csv"):
        df_market_data = pd.read_csv(file, sep=";")
        # set report_date as index
        df_market_data["report_date"] = pd.to_datetime(
            df_market_data["report_date"]
        ).dt.tz_localize(Settings.system_time_zone)
        df_market_data = df_market_data.set_index("report_date")

        # Loop over each row in df_market_data
        for index, row in df_market_data.iterrows():
            all_data.append(
                MarketDataModel(
                    isin_code=row["isin_code"],
                    report_date=index,
                    close_price=row["price"],
                    date_added=datetime.now(UTC),
                    source=row["source"],
                )
            )

        async with AsyncMarketDataDB() as db:
            # Store the data in the database
            try:
                await db.async_store_market_data(all_data)
            except IntegrityError:
                LOGGER.warning(f"Error parsing {file}. Skipping.")
                continue

    LOGGER.info(f"Stored {len(all_data)} records from CSV files to the database")


async def async_load_market_data_config() -> list[Source]:
    """Load market data settings files."""
    output_data: list[Source] = []
    with Settings.file_market_data_config.open(encoding="UTF-8") as file:
        # Load the YAML content from the file
        yaml_data = yaml.safe_load(file)

        global_sources = Sources(**yaml_data).sources
        LOGGER.info(f"Found {len(global_sources)} source(s) in global file")
        output_data.extend(global_sources)

    if (
        Settings.file_market_data_config_local
        and Settings.file_market_data_config_local.exists()
    ):
        with Settings.file_market_data_config_local.open(encoding="UTF-8") as file:
            # Load the YAML content from the file
            yaml_data = yaml.safe_load(file)

            local_sources = Sources(**yaml_data).sources
            LOGGER.info(f"Found {len(local_sources)} source(s) in local file")
            output_data.extend(local_sources)

    return output_data


async def async_get_market_data(isin_code: str | None = None) -> pd.DataFrame:
    """
    Get market data from database.

    Returns df with columns isin_code, price, date_added_utc, source.
    """
    async with AsyncMarketDataDB() as db:
        data = await db.async_filter_all(isin_code=isin_code)

        if not data:
            return pd.DataFrame()

        data_as_dict = [
            {
                "isin_code": record.isin_code,
                "price": record.close_price,
                "report_date": record.report_date,
                "date_added_utc": record.date_added,
                "source": record.source,
            }
            for record in data
        ]

        # Convert the data to a DataFrame
        df_data = pd.DataFrame(data_as_dict)

        # Convert the 'report_date' column to datetime and set it as the index
        df_data["report_date"] = pd.to_datetime(df_data["report_date"]).dt.tz_localize(
            Settings.system_time_zone
        )
        return df_data.set_index("report_date")


async def async_get_last_market_data_df() -> pd.DataFrame:
    """Return a DataFrame with the last found value per ISIN code."""
    async with AsyncMarketDataDB() as db:
        # Get the last market data for all ISIN codes
        data = await db.async_get_last_close_price_by_isin()

    df_data = pd.DataFrame(data, columns=["isin_code", "report_date", "price"])
    df_data["report_date"] = pd.to_datetime(df_data["report_date"]).dt.tz_localize(
        Settings.system_time_zone
    )
    return df_data.set_index("report_date")


@strawberry.type
@dataclass
class MarketDataOverviewRecord:
    """Market data overview record."""

    isin_code: str
    name: str | None
    first_date: date | None
    last_date: date | None
    currency: str | None


async def async_get_market_data_overview() -> list[MarketDataOverviewRecord]:
    """Return an overview of the market data."""
    sources = await async_load_market_data_config()
    all_security = await async_security_map_isin_to_security()

    output_data: list[MarketDataOverviewRecord] = []

    # For each source, get first and last date or market data
    for source in sources:
        df_market_data = await async_get_market_data(isin_code=source.isin_code)

        # Add the name of the security to the source
        security_obj = all_security.get(source.isin_code)
        name = security_obj.name if security_obj else source.name
        currency = security_obj.currency if security_obj else None

        # first_date should be None if the index min is nan
        if pd.isna(df_market_data.index.min()):
            first_date = None
        else:
            first_date = pd.to_datetime(df_market_data.index.min()).date()

        # last_date should be None if the index max is nan
        if pd.isna(df_market_data.index.max()):
            last_date = None
        else:
            last_date = pd.to_datetime(df_market_data.index.max()).date()

        output_data.append(
            MarketDataOverviewRecord(
                isin_code=source.isin_code,
                name=name,
                first_date=first_date,
                last_date=last_date,
                currency=currency,
            )
        )

    # Sort output data by name
    return sorted(output_data, key=lambda x: x.name if x.name else "")


def _class_importer(name: str) -> type[BaseMarketDataLoader] | None:
    """Load a class from a string representing a fully qualified class name."""
    # Split the class path into its individual components.
    components = name.split(".")
    class_name = components.pop()
    module_name = ".".join(components)

    try:
        module = import_module(module_name)
        return cast("type", getattr(module, class_name))
    except ModuleNotFoundError:
        LOGGER.exception(f"Module '{module_name}' not found.")
    except AttributeError:
        LOGGER.exception(f"Class '{class_name}' not found in module '{module_name}")

    return None


async def async_download_market_data() -> None:
    """Load JSON-data from a source."""
    sources = await async_load_market_data_config()

    for idx, source in enumerate(sources):
        loader_class = source.loader_class
        LOGGER.info(f"{idx}: Parsing {source.isin_code} using {loader_class}")

        if "plugin" in loader_class:
            LOGGER.info(f"Using plugin {loader_class}")
            loader_class_full_path = loader_class.replace("plugin", "pypmanager_plugin")
        else:
            loader_class_full_path = f"pypmanager.ingest.market_data.{loader_class}"

        try:
            data_loader_klass = _class_importer(loader_class_full_path)
        except AttributeError as err:
            msg = "Unable to load data"
            raise DataError(msg, err) from err

        if data_loader_klass is None:
            continue

        try:
            loader = data_loader_klass(
                lookup_key=source.lookup_key,
                isin_code=source.isin_code,
                name=source.name,
            )
            data_list = loader.to_source_data()

            async with AsyncMarketDataDB() as db:
                db_data_list: list[MarketDataModel] = []
                db_data_list = [
                    MarketDataModel(
                        isin_code=record.isin_code,
                        report_date=record.report_date,
                        close_price=record.price,
                        date_added=datetime.now(UTC),
                        source=loader.source,
                    )
                    for record in data_list
                ]
                await db.async_store_market_data(db_data_list)
        except HTTPError:
            LOGGER.exception(f"HTTP error when loading {loader}")
        except AttributeError:
            LOGGER.exception(f"Unable to load {loader}")

        # Sleep for a random amount of time between 1 and 5 seconds to avoid spamming
        # APIs
        await sleep(randint(1, 5))  # noqa: S311
