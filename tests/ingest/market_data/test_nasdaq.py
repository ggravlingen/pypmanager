"""Test loader for market data."""

from datetime import datetime
import json
from unittest import mock

from pypmanager.ingest.market_data.models import SourceData
from pypmanager.ingest.market_data.nasdaq import NasdaqLoader


def test_nasdaq_loader() -> None:
    """Test loading data from Nasdaq."""
    response_data = {
        "data": {
            "CP": [
                {
                    "x": 1739550060,
                    "y": 318.925,
                    "z": {"dateTime": "17:21 CET", "value": "318.925"},
                }
            ],
            "chartData": {
                "company": "Abc 123",
            },
        }
    }
    with mock.patch(
        "pypmanager.ingest.market_data.base_loader.requests.get",
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = json.dumps(response_data)

        loader = NasdaqLoader("abc123", "sample_key")
        loader.get_response()

        assert loader.raw_response == response_data
        assert loader.source == "Nasdaq"
        assert loader.extra_headers == {
            "Content-Type": "application/json; charset=utf-8"
        }
        assert loader.full_url == (
            "https://api.nasdaq.com/api/nordic/instruments/sample_key/"
            "chart?assetClass=SHARES&lang=en"
        )

        expected_source_data = [
            SourceData(
                report_date=datetime(2025, 2, 14, 16, 21),  # noqa: DTZ001
                isin_code="sample_key",
                name="Abc 123",
                price=318.925,
            )
        ]
        assert loader.to_source_data() == expected_source_data
