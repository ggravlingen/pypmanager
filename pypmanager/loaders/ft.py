"""Financial Times markets loader."""
from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import Any

import requests

from pypmanager.market_data_loader import SourceData

LOGGER = logging.getLogger(__name__)


class FTLoader:
    """Load data from Financial Times."""

    GET_DAYS = 365

    url = "https://markets.ft.com/data/chartapi/series"
    raw_response: dict[str, Any]

    def __init__(self, symbol: str, isin_code: str) -> None:
        """Init class."""
        self.symbol = symbol
        self.isin_code = isin_code

        self.get_response()
        self.to_source_data()

    @property
    def headers(self) -> dict[str, str]:
        """Return headers."""
        return {"Content-Type": "application/json"}

    def get_payload(self) -> dict[str, Any]:
        """Get payload."""
        return {
            "days": self.GET_DAYS,
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
                    "Symbol": self.symbol,
                    "OverlayIndicators": [],
                    "Params": {},
                }
            ],
        }

    def get_response(self) -> None:
        """Get reqponse."""
        response = requests.post(
            self.url,
            data=json.dumps(self.get_payload()),
            headers=self.headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = json.loads(response.text)

            self.raw_response = data

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
