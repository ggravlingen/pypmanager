"""Tests for ingest.market_data.morningstar."""

from __future__ import annotations

from datetime import datetime
import json
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from pypmanager.ingest.market_data.const import HttpResponseCodeLabels
from pypmanager.ingest.market_data.models import SourceData
from pypmanager.ingest.market_data.morningstar import (
    MorningstarLoader,
    MorningstarLoaderSHB,
)

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_morningstar_data_response() -> Generator[None, None, None]:
    """Mock response."""
    response_data = {
        "TimeSeries": {
            "Security": [
                {
                    "HistoryDetail": [
                        {"EndDate": "2024-12-23", "Value": "288.7028"},
                        {"EndDate": "2024-12-27", "Value": "288.1284"},
                        {"EndDate": "2024-12-30", "Value": "286.3586"},
                    ],
                    "Id": "F0GBR04M88",
                }
            ]
        }
    }
    with mock.patch(
        "pypmanager.ingest.market_data.base_loader.requests.get",
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = HttpResponseCodeLabels.OK
        mock_response.text = json.dumps(response_data)
        yield


@pytest.fixture
def mock_morningstar_shb_data_response() -> Generator[None, None, None]:
    """Mock response."""
    with mock.patch(
        "pypmanager.ingest.market_data.base_loader.requests.get",
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = HttpResponseCodeLabels.OK
        mock_response.content = b"test"
        yield


@pytest.mark.usefixtures("mock_morningstar_data_response")
def test_morningstar_loader__full_url() -> None:
    """Test MorningstarLoader.full_url."""
    loader = MorningstarLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.full_url == (
        "https://tools.morningstar.se/api/rest.svc/timeseries_price/"
        "n4omw1k3rh?id=535627197&currencyId=SEK&idtype=Morningstar&"
        "frequency=daily&startDate=2024-07-06&endDate=2025-01-02&outputType=JSON"
    )


@pytest.mark.usefixtures("mock_morningstar_data_response")
def test_morningstar_loader__source() -> None:
    """Test MorningstarLoader.source."""
    loader = MorningstarLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.source == "Morningstar"


@pytest.mark.usefixtures("mock_morningstar_data_response")
def test_morningstar_loader__get_response() -> None:
    """Test MorningstarLoader.get_response."""
    loader = MorningstarLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    loader.get_response()
    assert loader.raw_response == {
        "TimeSeries": {
            "Security": [
                {
                    "HistoryDetail": [
                        {"EndDate": "2024-12-23", "Value": "288.7028"},
                        {"EndDate": "2024-12-27", "Value": "288.1284"},
                        {"EndDate": "2024-12-30", "Value": "286.3586"},
                    ],
                    "Id": "F0GBR04M88",
                }
            ]
        }
    }


@pytest.mark.usefixtures("mock_morningstar_data_response")
def test_morningstar_loader__to_source_data() -> None:
    """Test MorningstarLoader.to_source_data."""
    loader = MorningstarLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.to_source_data() == [
        SourceData(
            report_date=datetime(2024, 12, 23, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="test",
            price="288.7028",
        ),
        SourceData(
            report_date=datetime(2024, 12, 27, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="test",
            price="288.1284",
        ),
        SourceData(
            report_date=datetime(2024, 12, 30, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="test",
            price="286.3586",
        ),
    ]


@pytest.mark.usefixtures("mock_morningstar_data_response")
def test_morningstar_loader__to_source_data__no_name() -> None:
    """Test MorningstarLoader.to_source_data with no name."""
    loader = MorningstarLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name=None,
    )
    assert loader.to_source_data() == []


@pytest.mark.usefixtures("mock_morningstar_shb_data_response")
def test_morningstar_loader_shb__full_url() -> None:
    """Test MorningstarLoaderSHB.full_url."""
    loader = MorningstarLoaderSHB(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.full_url == (
        "https://handelsbanken.fondlista.se/shb/sv/history/onefund.xls?fundid=535627197"
    )


@pytest.mark.usefixtures("mock_morningstar_shb_data_response")
def test_morningstar_loader_shb__source() -> None:
    """Test MorningstarLoaderSHB.source."""
    loader = MorningstarLoaderSHB(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.source == "Svenska Handelsbanken"
