"""Avanza loader."""

from __future__ import annotations

from datetime import datetime

from .base_loader import BaseMarketDataLoader
from .models import SourceData


class AvanzaLoader(BaseMarketDataLoader):
    """Load data from Avanza."""

    url = "https://www.avanza.se/_api/fund-guide/guide/"

    @property
    def full_url(self: AvanzaLoader) -> str:
        """Return full URL, including lookup key."""
        return f"{self.url}{self.lookup_key}"

    def get_response(self: AvanzaLoader) -> None:
        """Get response."""
        data = self.query_endpoint()
        self.raw_response = data

    @property
    def source(self: AvanzaLoader) -> str:
        """Get name of source."""
        return "Avanza"

    def to_source_data(self: AvanzaLoader) -> list[SourceData]:
        """Convert to SourceData."""
        return [
            SourceData(
                report_date=datetime.strptime(  # noqa: DTZ007
                    self.raw_response["navDate"], "%Y-%m-%dT%H:%M:%S"
                ),
                isin_code=self.isin_code,
                price=self.raw_response["nav"],
                name=self.raw_response["name"],
            )
        ]
