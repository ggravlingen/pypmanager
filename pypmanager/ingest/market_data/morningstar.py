"""Morningstar loader."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from io import BytesIO

import pandas as pd
import requests

from pypmanager.const import HttpStatusCodes

from .base_loader import BaseMarketDataLoader
from .const import LOAD_HISTORY_DAYS, LOGGER
from .models import SourceData


class MorningstarLoader(BaseMarketDataLoader):
    """Load data from Morningstar."""

    start_date = (datetime.now(UTC) - timedelta(days=LOAD_HISTORY_DAYS)).strftime(
        "%Y-%m-%d",
    )
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    currency = "SEK"

    url = (
        "https://tools.morningstar.se/api/rest.svc/timeseries_price/n4omw1k3rh?"
        "id={lookup_key}&currencyId={currency}&idtype=Morningstar&frequency=daily"
        "&startDate={start_date}&endDate={end_date}&outputType=JSON"
    )

    @property
    def full_url(self: MorningstarLoader) -> str:
        """Return full URL, including lookup key."""
        return self.url.format(
            lookup_key=self.lookup_key,
            start_date=self.start_date,
            end_date=self.end_date,
            currency=self.currency,
        )

    def get_response(self: MorningstarLoader) -> None:
        """Get response."""
        data = self.query_endpoint()
        self.raw_response = data

    @property
    def source(self: MorningstarLoader) -> str:
        """Get name of source."""
        return "Morningstar"

    def to_source_data(self: MorningstarLoader) -> list[SourceData]:
        """Convert to SourceData."""
        data_list = self.raw_response["TimeSeries"]["Security"][0]["HistoryDetail"]

        if self.name is None:
            return []

        return [
            SourceData(
                report_date=datetime.strptime(row["EndDate"], "%Y-%m-%d"),  # noqa: DTZ007
                isin_code=self.isin_code,
                price=row["Value"],
                name=self.name,
            )
            for row in data_list
        ]


class MorningstarLoaderSHB(BaseMarketDataLoader):
    """
    Load data from Morningstar's white label for funds.

    Even though the endpoint says xlsx, data is really returned as a HTML table.
    """

    url = "https://handelsbanken.fondlista.se/shb/sv/history/onefund.xls"

    @property
    def full_url(self: MorningstarLoaderSHB) -> str:
        """Return full URL, including lookup key."""
        return f"{self.url}?fundid={self.lookup_key}"

    def get_response(self: MorningstarLoaderSHB) -> None:
        """Get reqponse."""
        response = requests.get(self.full_url, timeout=10)

        if response.status_code == HttpStatusCodes.OK:
            self.raw_response_io = BytesIO(response.content)
        else:
            LOGGER.warning("Unable to load data")

    @property
    def source(self: MorningstarLoaderSHB) -> str:
        """Get name of source."""
        return "Svenska Handelsbanken"

    def to_source_data(self: MorningstarLoaderSHB) -> list[SourceData]:
        """Convert to SourceData."""
        output_data: list[SourceData] = []
        df_tables = pd.read_excel(
            self.raw_response_io,
            thousands=" ",
            decimal=",",
            parse_dates=True,
        )

        for _, row in df_tables.iterrows():
            output_data.append(
                SourceData(
                    report_date=datetime.strptime(row["Datum"], "%Y-%m-%d"),  # noqa: DTZ007
                    isin_code=self.isin_code,
                    name=row["Namn"],
                    price=row["Kurs"],
                ),
            )

        return output_data
