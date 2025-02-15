"""Financial Times markets loader."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any

import requests

from pypmanager.const import HttpStatusCodes

from .base_loader import BaseMarketDataLoader
from .models import SourceData


class LevlerLoader(BaseMarketDataLoader):
    """Load data from Levler.se."""

    full_url = "https://levler.se/api/open/funds/GetFundDetails"

    @property
    def extra_headers(self: LevlerLoader) -> dict[str, str] | None:
        """Return headers."""
        return {"Content-Type": "application/json"}

    def get_payload(self: LevlerLoader) -> dict[str, Any]:
        """Get payload."""
        return {
            "orderBookKey": {
                "isin": self.isin_code,
                "currencyCode": "USD",
                "mic": "FUND",
            }
        }

    def get_response(self: LevlerLoader) -> None:
        """Get reqponse."""
        response = requests.post(
            self.full_url,
            data=json.dumps(self.get_payload()),
            headers=self.headers,
            timeout=self.TIMEOUT_SECOND,
        )
        response.raise_for_status()
        if response.status_code == HttpStatusCodes.OK:
            self.raw_response = json.loads(response.text)

    @property
    def source(self: LevlerLoader) -> str:
        """Get name of source."""
        return "Levler"

    def to_source_data(self: LevlerLoader) -> list[SourceData]:
        """Convert to SourceData."""
        name = self.raw_response["fund"]["name"]
        output_list: list[SourceData] = []

        for data in self.raw_response["fund"]["navSeries"]["values"]:
            report_date = datetime.strptime(data["d"], "%y%m%d")  # noqa: DTZ007
            output_list.append(
                SourceData(
                    report_date=report_date,
                    isin_code=self.isin_code,
                    name=name,
                    price=data["v"],
                ),
            )

        return output_list
