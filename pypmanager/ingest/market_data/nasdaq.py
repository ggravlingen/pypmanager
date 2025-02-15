"""Nasdaq loader."""

from __future__ import annotations

from datetime import datetime

from .base_loader import BaseMarketDataLoader
from .models import SourceData


class NasdaqLoader(BaseMarketDataLoader):
    """Load data from Nasdaq."""

    URL_TEMPLATE = (
        "https://api.nasdaq.com/api/nordic/instruments/{symbol}/"
        "chart?assetClass=SHARES&lang=en"
    )

    @property
    def headers(self: NasdaqLoader) -> dict[str, str]:
        """Return headers."""
        return {"Content-Type": "application/json; charset=utf-8"}

    @property
    def full_url(self: NasdaqLoader) -> str:
        """Return full URL, including lookup key."""
        return self.URL_TEMPLATE.format(symbol=self.lookup_key)

    def get_response(self: NasdaqLoader) -> None:
        """Get response."""
        data = self.query_endpoint()
        self.raw_response = data

    @property
    def source(self: NasdaqLoader) -> str:
        """Get name of source."""
        return "Nasdaq"

    def to_source_data(self: NasdaqLoader) -> list[SourceData]:
        """Convert to SourceData."""
        company = self.raw_response["data"]["chartData"]["company"]
        output_list: list[SourceData] = []

        for row in self.raw_response["data"]["CP"]:
            report_date = datetime.fromtimestamp(row["x"])  # noqa: DTZ006
            output_list.append(
                SourceData(
                    report_date=report_date,
                    isin_code=self.lookup_key,
                    price=row["y"],
                    name=company,
                )
            )

        return output_list
