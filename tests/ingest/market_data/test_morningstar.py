"""Tests for ingest.market_data.morningstar."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

from freezegun import freeze_time
import pytest

from pypmanager.const import HttpStatusCodes
from pypmanager.ingest.market_data.models import SourceData
from pypmanager.ingest.market_data.morningstar import (
    MorningstarLoader,
    MorningstarLoaderSHB,
)

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_morningstar_data_response() -> Generator[None]:
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
        "pypmanager.ingest.market_data.base_loader.requests.Session.get",
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = HttpStatusCodes.OK
        mock_response.text = json.dumps(response_data)
        yield


@pytest.fixture
def mock_morningstar_shb_data_response() -> Generator[None]:
    """Mock response."""
    with mock.patch(
        "pypmanager.ingest.market_data.base_loader.requests.Session.get",
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = HttpStatusCodes.OK
        with Path("tests/fixtures/market_data/mstar_shb.xlsx").open("rb") as f:
            mock_response.content = f.read()
            yield


@pytest.mark.usefixtures("mock_morningstar_data_response")
def test_morningstar_loader__full_url() -> None:
    """Test MorningstarLoader.full_url."""
    with freeze_time("2025-01-03"):
        loader = MorningstarLoader(
            isin_code="SE0005796331",
            lookup_key="535627197",
            name="test",
        )
        assert loader.full_url == (
            "https://tools.morningstar.se/api/rest.svc/timeseries_price/"
            "n4omw1k3rh?id=535627197&currencyId=SEK&idtype=Morningstar&"
            "frequency=daily&startDate=2024-07-07&endDate=2025-01-03&outputType=JSON"
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


@pytest.mark.usefixtures("mock_morningstar_shb_data_response")
def test_morningstar_loader_shb__to_source_data() -> None:
    """Test MorningstarLoaderSHB.to_source_data."""
    loader = MorningstarLoaderSHB(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.to_source_data() == [
        SourceData(
            report_date=datetime(2020, 1, 3, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="Handelsbanken Sverige 100 Index Criteria",
            price=279.13,
        ),
        SourceData(
            report_date=datetime(2020, 1, 2, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="Handelsbanken Sverige 100 Index Criteria",
            price=282.22,
        ),
    ]
