"""Morningstar loader."""

from datetime import datetime
import json

import requests

from .base_loader import BaseMarketDataLoader
from .const import LOGGER
from .models import SourceData


class MorningstarLoader(BaseMarketDataLoader):
    """Load data from Morningstar."""

    start_date = "2023-01-01"
    end_date = "2023-12-31"
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
        """Get reqponse."""
        response = requests.get(self.full_url, timeout=10)

        if response.status_code == 200:
            data = json.loads(response.text)

            self.raw_response = data
        else:
            LOGGER.warning("Unable to load data")

    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
        data_list = self.raw_response["TimeSeries"]["Security"][0]["HistoryDetail"]

        output_list: list[SourceData] = []
        for row in data_list:
            assert self.name is not None

            output_list.append(
                SourceData(
                    report_date=datetime.strptime(row["EndDate"], "%Y-%m-%d"),
                    isin_code=self.isin_code,
                    price=row["Value"],
                    name=self.name,
                )
            )

        return output_list
