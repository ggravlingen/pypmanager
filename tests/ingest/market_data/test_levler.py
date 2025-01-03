"""Tests for ingest.market_data.levler."""

from __future__ import annotations

from datetime import datetime
import json
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from pypmanager.const import HttpStatusCodes
from pypmanager.ingest.market_data.levler import LevlerLoader
from pypmanager.ingest.market_data.models import SourceData

if TYPE_CHECKING:
    from collections.abc import Generator

SAMPLE_RESPONSE = {
    "fund": {
        "name": "SEB Global Indexnära C USD - Lux",
        "navSeries": {
            "values": [
                {"v": 30.274925, "d": "250102"},
            ]
        },
    }
}


@pytest.fixture
def mock_levler_data_response() -> Generator[None, None, None]:
    """Mock response."""
    with mock.patch(
        "pypmanager.ingest.market_data.base_loader.requests.post"
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = HttpStatusCodes.OK
        mock_response.text = json.dumps(SAMPLE_RESPONSE)
        yield


@pytest.mark.usefixtures("mock_levler_data_response")
def test_header() -> None:
    """Test LevlerLoader.headers."""
    loader = LevlerLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.headers == {"Content-Type": "application/json"}


@pytest.mark.usefixtures("mock_levler_data_response")
def test_source() -> None:
    """Test LevlerLoader.source."""
    loader = LevlerLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.source == "Levler"


@pytest.mark.usefixtures("mock_levler_data_response")
def test_get_payload() -> None:
    """Test LevlerLoader.get_payload."""
    loader = LevlerLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.get_payload() == {
        "orderBookKey": {
            "isin": "SE0005796331",
            "currencyCode": "USD",
            "mic": "FUND",
        }
    }


@pytest.mark.usefixtures("mock_levler_data_response")
def test_to_source_data() -> None:
    """Test LevlerLoader.to_source_data."""
    loader = LevlerLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.to_source_data() == [
        SourceData(
            report_date=datetime(2025, 1, 2, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="SEB Global Indexnära C USD - Lux",
            price=30.274925,
        )
    ]
