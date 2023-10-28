"""Morningstar loader."""

from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import requests

from pypmanager.const import HttpResponseCodeLabels

from .base_loader import BaseMarketDataLoader
from .const import LOAD_HISTORY_DAYS, LOGGER
from .models import SourceData


class MorningstarLoader(BaseMarketDataLoader):
    """Load data from Morningstar."""

    start_date = (datetime.utcnow() - timedelta(days=LOAD_HISTORY_DAYS)).strftime(
        "%Y-%m-%d"
    )
    end_date = datetime.utcnow().strftime("%Y-%m-%d")
    currency = "SEK"

    url = (
        "https://tools.morningstar.se/api/rest.svc/timeseries_price/n4omw1k3rh?"
        "id={lookup_key}&currencyId={currency}&idtype=Morningstar&frequency=daily"
        "&startDate={start_date}&endDate={end_date}&outputType=JSON"
    )

    @property
    def full_url(self) -> str:
        """Return full URL, including lookup key."""
        return self.url.format(
            lookup_key=self.lookup_key,
            start_date=self.start_date,
            end_date=self.end_date,
            currency=self.currency,
        )

    def get_response(self) -> None:
        """Get response."""
        data = self.query_endpoint()
        self.raw_response = data

    @property
    def source(self) -> str:
        """Get name of source."""
        return "Morningstar"

    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
        data_list = self.raw_response["TimeSeries"]["Security"][0]["HistoryDetail"]

        output_list: list[SourceData] = []
        if self.name is None:
            return output_list

        for row in data_list:
            output_list.append(
                SourceData(
                    report_date=datetime.strptime(row["EndDate"], "%Y-%m-%d"),
                    isin_code=self.isin_code,
                    price=row["Value"],
                    name=self.name,
                )
            )

        return output_list


class MorningstarLoaderSHB(BaseMarketDataLoader):
    """
    Load data from Morningstar's white label for funds.

    Even though the endpoint says xlsx, data is really returned as a HTML table.
    """

    url = "https://secure.msse.se/shb/sv.se/history/onefund.xlsx"

    @property
    def full_url(self) -> str:
        """Return full URL, including lookup key."""
        return f"{self.url}?fundid={self.lookup_key}"

    def get_response(self) -> None:
        """Get reqponse."""
        response = requests.get(self.full_url, timeout=10)

        if response.status_code == HttpResponseCodeLabels.OK:
            self.raw_response_io = BytesIO(response.content)
        else:
            LOGGER.warning("Unable to load data")

    @property
    def source(self) -> str:
        """Get name of source."""
        return "Svenska Handelsbanken"

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
