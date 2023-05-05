"""Loader for market data from Avanza."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os
from typing import Any

from numpy import datetime64
import pandas as pd
from pydantic import BaseModel
import requests
import yaml

from pypmanager.error import DataError
from pypmanager.settings import Settings
from pypmanager.utils import class_importer

CONFIG_FILE = os.path.abspath(os.path.join(Settings.DIR_DATA, "market_data.yaml"))

LOGGER = logging.getLogger(__name__)


@dataclass
class SourceData:
    """Represent source data."""

    report_date: datetime
    isin_code: str
    name: str
    price: float


class Source(BaseModel):
    """A source."""

    field_date: str | None
    field_isin: str | None
    field_nav: str | None
    field_name: str | None
    isin_code: str | None
    loader_class: str | None
    symbol: str | None
    url: str | None


class Sources(BaseModel):
    """Definition of sources."""

    sources: list[Source]


def _load_sources() -> list[Source]:
    """Load settings."""
    with open(CONFIG_FILE, encoding="UTF-8") as file:
        # Load the YAML content from the file
        yaml_data = yaml.safe_load(file)

        data = Sources(**yaml_data)

        return data.sources


def _extract_data(data: dict[str, Any], source: Source) -> list[SourceData]:
    """Extract data from a JSON object."""
    assert source.field_date is not None
    assert source.field_isin is not None
    assert source.field_nav is not None
    assert source.field_name is not None

    return [
        SourceData(
            report_date=datetime.strptime(data[source.field_date], "%Y-%m-%dT%H:%M:%S"),
            isin_code=data[source.field_isin],
            price=data[source.field_nav],
            name=data[source.field_name],
        )
    ]


def _upsert_df(data: list[SourceData]) -> None:
    """Upsert dataframe."""
    upsert_df = pd.DataFrame([vars(s) for s in data])

    column_dtypes = {"report_date": datetime64}
    # Check if the CSV file exists
    try:
        existing_df = pd.read_csv(
            Settings.FILE_MARKET_DATA,
            sep=";",
            parse_dates=["report_date"],
        )
    except FileNotFoundError:
        existing_df = pd.DataFrame(
            columns=["isin_code", "price", "report_date", "name"], dtype=column_dtypes
        )

    # Merge the existing DataFrame and the upsert DataFrame
    merged_df = pd.merge(
        existing_df,
        upsert_df,
        on=["isin_code", "report_date"],
        how="outer",
        suffixes=("", "_update"),
    )

    # Update the rows with the new values from the upsert DataFrame
    for column in merged_df.columns:
        if column.endswith("_update"):
            original_column = column[:-7]  # Remove the '_update' suffix
            merged_df[original_column].update(merged_df.pop(column))

    merged_df.sort_values(["isin_code", "report_date"], inplace=True)

    # Write the merged DataFrame back to the CSV file
    merged_df.to_csv(Settings.FILE_MARKET_DATA, index=False, sep=";")


def market_data_loader() -> None:
    """Load JSON-data from a source."""
    sources = _load_sources()

    for source in sources:
        if (
            source.loader_class
            and source.isin_code
            and source.symbol
            and source.url is None
        ):
            LOGGER.info(f"Parsing {source.isin_code} using {source.loader_class}")

            try:
                data_loader_klass = class_importer(source.loader_class)
            except AttributeError as err:
                raise DataError("Unable to load data", err) from err
            loader = data_loader_klass(symbol=source.symbol, isin_code=source.isin_code)
            _upsert_df(data=loader.to_source_data())
        else:
            LOGGER.info(f"Parsing {source.url}")

            assert source.url is not None

            response = requests.get(source.url, timeout=10)

            if response.status_code == 200:
                data = json.loads(response.text)
                extracted_data = _extract_data(data=data, source=source)
                _upsert_df(data=extracted_data)
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
