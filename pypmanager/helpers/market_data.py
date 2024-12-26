"""Helper functions for market data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import strawberry
import yaml

from pypmanager.error import DataError
from pypmanager.helpers.security import async_load_security_data
from pypmanager.ingest.market_data.models import Source, SourceData, Sources
from pypmanager.settings import Settings

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pypmanager.ingest.market_data.base_loader import BaseMarketDataLoader


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


def get_market_data(isin_code: str | None = None) -> pd.DataFrame:
    """
    Load all market data from CSV files and concatenate them into a single DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing all the market data concatenated together,
        indexed by 'report_date'. If isin_code is provided, only the data for that
        isin_code will be returned. In that case, the index is a datetime index.
    """
    all_data_frames: list[pd.DataFrame] = []

    for file in Settings.dir_market_data.glob("*.csv"):
        df_market_data = pd.read_csv(file, sep=";", index_col="report_date")
        all_data_frames.append(df_market_data)

    merged_df = pd.concat(all_data_frames, ignore_index=False)

    merged_df = merged_df.replace("nan", np.nan)
    merged_df = merged_df.replace({np.nan: None})

    if isin_code:
        df_queried = merged_df.query(f"isin_code == '{isin_code}'")
        # We want to merge the date range DataFrame with df_market_data on the date
        # index so we need to convert the index to datetime
        df_queried.index = pd.to_datetime(df_queried.index).tz_localize(
            Settings.system_time_zone
        )
        return df_queried

    return merged_df


@strawberry.type
@dataclass
class MarketDataOverviewRecord:
    """Market data overview record."""

    isin_code: str
    name: str | None
    first_date: date | None
    last_date: date | None


async def async_get_market_data_overview() -> list[MarketDataOverviewRecord]:
    """Return an overview of the market data."""
    sources = await async_load_market_data_config()
    all_security = await async_load_security_data()

    output_data: list[MarketDataOverviewRecord] = []

    # For each source, get first and last date or market data
    for source in sources:
        df_market_data = get_market_data(isin_code=source.isin_code)

        # Add the name of the security to the source
        security_obj = all_security.get(source.isin_code)
        name = security_obj.name if security_obj else source.name

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
            )
        )

    # Sort output data by name
    return sorted(output_data, key=lambda x: x.name if x.name else "")


def _class_importer(name: str) -> Any:  # noqa: ANN401
    """Load a class from a string representing a fully qualified class name."""
    # Split the class path into its individual components.
    components = name.split(".")
    class_name = components.pop()
    module_name = ".".join(components)

    # Dynamically load the module.
    module = __import__(module_name, fromlist=[class_name])

    # Get the class from the module.
    return getattr(module, class_name)


async def async_download_market_data() -> None:
    """Load JSON-data from a source."""
    sources = await async_load_market_data_config()

    for idx, source in enumerate(sources):
        LOGGER.info(f"{idx}: Parsing {source.isin_code} using {source.loader_class}")

        loader_class_full_path = f"pypmanager.ingest.market_data.{source.loader_class}"

        try:
            data_loader_klass = _class_importer(loader_class_full_path)
        except AttributeError as err:
            msg = "Unable to load data"
            raise DataError(msg, err) from err

        try:
            loader: BaseMarketDataLoader = data_loader_klass(
                lookup_key=source.lookup_key,
                isin_code=source.isin_code,
                name=source.name,
            )
            UpdateMarketDataCsv(data=loader.to_source_data(), source_name=loader.source)
        except AttributeError:
            LOGGER.exception(f"Unable to load {loader}")


class UpdateMarketDataCsv:
    """Helper class to update a CSV file containing market data."""

    df_all_data: pd.DataFrame
    df_existing_file: pd.DataFrame
    df_source_data: pd.DataFrame

    def __init__(
        self: UpdateMarketDataCsv, data: list[SourceData], source_name: str
    ) -> None:
        """Init class."""
        self.data = data
        self.source_name = source_name

        self.file_market_data = Settings.dir_market_data / f"{source_name}.csv"

        self.prepare_source_data()
        self.concat_data()
        self.save_to_csv()

    @property
    def target_file_exists(self: UpdateMarketDataCsv) -> bool:
        """Check if the target file exists."""
        return self.file_market_data.exists()

    def prepare_source_data(self: UpdateMarketDataCsv) -> None:
        """Convert source data to a data frame."""
        self.df_source_data = pd.DataFrame([vars(s) for s in self.data])

        # Add a timestamp for when we added the date
        self.df_source_data["date_added_utc"] = datetime.now(UTC)
        self.df_source_data["source"] = self.source_name

    def concat_data(self: UpdateMarketDataCsv) -> None:
        """Merge existing data, if existing, with new data."""
        if self.target_file_exists:
            existing_df = pd.read_csv(
                self.file_market_data,
                sep=";",
                parse_dates=["report_date"],
            )
        else:
            existing_df = pd.DataFrame(
                data=[],
                columns=["isin_code", "price", "report_date", "name", "date_added_utc"],
            )

        self.df_all_data = pd.concat([existing_df, self.df_source_data])

    def save_to_csv(self: UpdateMarketDataCsv) -> None:
        """Save data to CSV."""
        df_final_output = self.df_all_data.copy()

        # Remove duplicates
        df_final_output = df_final_output.drop_duplicates(
            subset=["isin_code", "report_date"], keep="last"
        )

        df_final_output = df_final_output.sort_values(["isin_code", "report_date"])

        # Write the merged DataFrame back to the CSV file
        df_final_output.to_csv(self.file_market_data, index=False, sep=";")
