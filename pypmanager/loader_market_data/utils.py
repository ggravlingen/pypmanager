"""Util functions."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from numpy import datetime64
import pandas as pd
import yaml

from pypmanager.settings import Settings

from .models import Source, SourceData, Sources


def _class_importer(name: str) -> Any:
    """
    Load a class from a string representing a fully qualified class name.

    :param class_path: The fully qualified name of the class to load and instantiate.
    :return: An instance of the specified class.
    """
    # Split the class path into its individual components.
    components = name.split(".")
    class_name = components.pop()
    module_name = ".".join(components)

    # Dynamically load the module.
    module = __import__(module_name, fromlist=[class_name])

    # Get the class from the module.
    return getattr(module, class_name)


def _load_sources() -> list[Source]:
    """Load settings."""
    with open(Settings.file_market_data_config, encoding="UTF-8") as file:
        # Load the YAML content from the file
        yaml_data = yaml.safe_load(file)

        data = Sources(**yaml_data)

        return data.sources


def _upsert_df(data: list[SourceData], source_name: str) -> None:
    """Upsert dataframe."""
    upsert_df = pd.DataFrame([vars(s) for s in data])

    # Add a timestamp for when we added the date
    upsert_df["date_added_utc"] = datetime.utcnow()
    upsert_df["source"] = source_name

    column_dtypes = {"report_date": datetime64}
    # Check if the CSV file exists
    try:
        existing_df = pd.read_csv(
            Settings.file_market_data,
            sep=";",
            parse_dates=["report_date"],
        )
    except FileNotFoundError:
        existing_df = pd.DataFrame(
            columns=["isin_code", "price", "report_date", "name", "date_added_utc"],
            dtype=column_dtypes,
        )

    # Merge the existing DataFrame and the upsert DataFrame
    merged_df = existing_df.merge(
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

    merged_df = merged_df.sort_values(["isin_code", "report_date"])

    # Write the merged DataFrame back to the CSV file
    merged_df.to_csv(Settings.file_market_data, index=False, sep=";")
