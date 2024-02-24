"""Financial Times markets loader."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any

import requests

from pypmanager.const import HttpResponseCodeLabels
from pypmanager.loader_market_data.const import LOAD_HISTORY_DAYS

from .base_loader import BaseMarketDataLoader
from .models import SourceData


class FTLoader(BaseMarketDataLoader):
    """Load data from Financial Times."""

    full_url = "https://markets.ft.com/data/chartapi/series"

    @property
    def headers(self) -> dict[str, str]:
        """Return headers."""
        return {"Content-Type": "application/json"}

    def get_payload(self) -> dict[str, Any]:
        """Get payload."""
        return {
            "days": LOAD_HISTORY_DAYS,
            "dataNormalized": False,
            "dataPeriod": "Day",
            "dataInterval": 1,
            "realtime": False,
            "yFormat": "0.###",
            "timeServiceFormat": "JSON",
            "rulerIntradayStart": 26,
            "rulerIntradayStop": 3,
            "rulerInterdayStart": 10957,
            "rulerInterdayStop": 365,
            "returnDateType": "ISO8601",
            "elements": [
                {
                    "Type": "price",
                    "Symbol": self.lookup_key,
                    "OverlayIndicators": [],
                    "Params": {},
                }
            ],
        }

    def get_response(self) -> None:
        """Get reqponse."""
        response = requests.post(
            self.full_url,
            data=json.dumps(self.get_payload()),
            headers=self.headers,
            timeout=10,
        )
        if response.status_code == HttpResponseCodeLabels.OK:
            data = json.loads(response.text)

            self.raw_response = data

    @property
    def source(self) -> str:
        """Get name of source."""
        return "Financial Times"

    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
        name = self.raw_response["Elements"][0]["CompanyName"]
        output_list: list[SourceData] = []
        dates = self.raw_response["Dates"]
        close = self.raw_response["Elements"][0]["ComponentSeries"][3]["Values"]
        for idx, _ in enumerate(self.raw_response["Dates"]):
            output_list.append(
                SourceData(
                    report_date=datetime.strptime(dates[idx], "%Y-%m-%dT%H:%M:%S"),
                    isin_code=self.isin_code,
                    name=name,
                    price=close[idx],
                )
            )

        return output_list
