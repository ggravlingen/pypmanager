"""Test loader for market data."""
from datetime import datetime
import json
from unittest import mock

from pypmanager.loader_market_data.avanza import AvanzaLoader
from pypmanager.loader_market_data.models import SourceData


def test_avanza_loader():
    """Test loading data from Avanza."""
    response_data = {
        "navDate": "2023-05-14T12:00:00",
        "nav": 100.0,
        "name": "Sample Fund",
    }
    with mock.patch("pypmanager.loader_market_data.avanza.requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = json.dumps(response_data)

        loader = AvanzaLoader("abc123", "sample_key")
        loader.get_response()

        assert loader.raw_response == response_data
        assert loader.source == "Avanza"

        expected_source_data = [
            SourceData(
                report_date=datetime.strptime(
                    "2023-05-14T12:00:00", "%Y-%m-%dT%H:%M:%S"
                ),
                isin_code="abc123",
                price=100.0,
                name="Sample Fund",
            )
        ]
        assert loader.to_source_data() == expected_source_data
