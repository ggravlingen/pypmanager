"""Load data from Handelsbanker Fonder."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO

import pandas as pd
import requests

from .base_loader import BaseMarketDataLoader
from .const import LOGGER
from .models import SourceData


class SHBFonderLoader(BaseMarketDataLoader):
    """
    Load data from Handelsbanken Fonder.

    Even though the endpoint says xls, data is really returned as a HTML table.
    """

    url = "https://secure.msse.se/shb/sv.se/history/onefund.xls"

    @property
    def full_url(self) -> str:
        """Return full URL, including lookup key."""
        return f"{self.url}?fundid={self.lookup_key}"

    def get_response(self) -> None:
        """Get reqponse."""
        response = requests.get(self.full_url, timeout=10)

        if response.status_code == 200:
            self.raw_response_io = BytesIO(response.content)
        else:
            LOGGER.warning("Unable to load data")

    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
        output_data: list[SourceData] = []
        df_tables = pd.read_html(
            self.raw_response_io,
            thousands=" ",
            decimal=",",
            parse_dates=True,
        )

        # There is only one table
        data_table = df_tables[0]

        for _, row in data_table.iterrows():
            output_data.append(
                SourceData(
                    report_date=datetime.strptime(row["Datum"], "%Y-%m-%d"),
                    isin_code=self.isin_code,
                    name=row["Namn"],
                    price=row["Kurs"],
                )
            )

        return output_data
