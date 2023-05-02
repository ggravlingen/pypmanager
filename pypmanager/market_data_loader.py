"""Loader for market data from Avanza."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
import os
from typing import Any

from numpy import datetime64
import pandas as pd
from pydantic import BaseModel
import requests
import yaml

from pypmanager.settings import Settings

CONFIG_FILE = os.path.abspath(os.path.join(Settings.DIR_DATA, "market_data.yaml"))


@dataclass
class SourceData:
    """Represent source data."""

    report_date: datetime
    isin_code: str
    name: str
    price: float


class Source(BaseModel):
    """A source."""

    field_date: str
    field_isin: str
    field_nav: str
    field_name: str
    url: str


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


def _extract_data(data: dict[str, Any], source: Source) -> SourceData:
    """Extract data from a JSON object."""
    return SourceData(
        report_date=datetime.strptime(data[source.field_date], "%Y-%m-%dT%H:%M:%S"),
        isin_code=data[source.field_isin],
        price=data[source.field_nav],
        name=data[source.field_name],
    )


def _upsert_df(data: SourceData) -> None:
    """Upsert dataframe."""
    upsert_df = pd.DataFrame([asdict(data)])

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

    # Write the merged DataFrame back to the CSV file
    merged_df.to_csv(Settings.FILE_MARKET_DATA, index=False, sep=";")


def market_data_loader():
    """Load JSON-data from a source."""
    sources = _load_sources()

    for source in sources:
        response = requests.get(source.url, timeout=10)

        if response.status_code == 200:
            data = json.loads(response.text)
            extracted_data = _extract_data(data=data, source=source)
            _upsert_df(data=extracted_data)
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
