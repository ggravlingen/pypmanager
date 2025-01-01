"""Tests for ingest.market_data.ft."""

from __future__ import annotations

from datetime import datetime
import json
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from pypmanager.ingest.market_data.const import HttpResponseCodeLabels
from pypmanager.ingest.market_data.ft import FTLoader
from pypmanager.ingest.market_data.models import SourceData

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_ft_data_response() -> Generator[FTLoader, None, None]:
    """Mock response."""
    response_data = {
        "Dates": ["2024-12-23T00:00:00", "2024-12-27T00:00:00", "2024-12-30T00:00:00"],
        "NormalizeDate": "2024-12-20T00:00:00",
        "NormalizeValues": {
            "Date": "2024-12-20T00:00:00",
            "Close": 285.81,
            "Open": 285.81,
            "High": 285.81,
            "Low": 285.81,
        },
        "Status": 1,
        "StatusString": "Success",
        "MetaData": {"TimingRender": 0.0},
        "TimeService": {
            "TradingDays": [
                # This list is abbreviated for brevity.
                "2025-12-31T00:00:00",
            ],
            "Status": 1,
        },
        "Elements": [
            {
                "Label": "Price",
                "Type": "price",
                "CompanyName": "Handelsbanken H\u00e5llbar Energi (A1 SEK)",
                "IssueType": "OF",
                "Symbol": "535679922",
                "Status": 1,
                "UtcOffsetMinutes": -300,
                "ExchangeId": "LIP",
                "Currency": "SEK",
                "Meta": {},
                "OverlayIndicators": [],
                "ComponentSeries": [
                    {
                        "Type": "Open",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                    {
                        "Type": "High",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                    {
                        "Type": "Low",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                    {
                        "Type": "Close",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                ],
                "TimeZoneLabel": "EST",
                "DisplaySymbol": "",
            }
        ],
    }
    with mock.patch(
        "pypmanager.ingest.market_data.base_loader.requests.post",
    ) as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = HttpResponseCodeLabels.OK
        mock_response.text = json.dumps(response_data)
        yield


@pytest.mark.usefixtures("mock_ft_data_response")
def test_ft_loader__headers() -> None:
    """Test FTLoader.headers."""
    loader = FTLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.headers == {"Content-Type": "application/json"}


@pytest.mark.usefixtures("mock_ft_data_response")
def test_ft_loader__source() -> None:
    """Test FTLoader.source."""
    loader = FTLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.source == "Financial Times"


@pytest.mark.usefixtures("mock_ft_data_response")
def test_ft_loader__raw_response() -> None:
    """Test FTLoader.raw_response."""
    loader = FTLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )
    assert loader.raw_response == {
        "Dates": ["2024-12-23T00:00:00", "2024-12-27T00:00:00", "2024-12-30T00:00:00"],
        "NormalizeDate": "2024-12-20T00:00:00",
        "NormalizeValues": {
            "Date": "2024-12-20T00:00:00",
            "Close": 285.81,
            "Open": 285.81,
            "High": 285.81,
            "Low": 285.81,
        },
        "Status": 1,
        "StatusString": "Success",
        "MetaData": {"TimingRender": 0.0},
        "TimeService": {"TradingDays": ["2025-12-31T00:00:00"], "Status": 1},
        "Elements": [
            {
                "Label": "Price",
                "Type": "price",
                "CompanyName": "Handelsbanken Hållbar Energi (A1 SEK)",
                "IssueType": "OF",
                "Symbol": "535679922",
                "Status": 1,
                "UtcOffsetMinutes": -300,
                "ExchangeId": "LIP",
                "Currency": "SEK",
                "Meta": {},
                "OverlayIndicators": [],
                "ComponentSeries": [
                    {
                        "Type": "Open",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                    {
                        "Type": "High",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                    {
                        "Type": "Low",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                    {
                        "Type": "Close",
                        "MaxValue": 290.92,
                        "MinValue": 287.63,
                        "MaxValueDate": "2024-12-27T00:00:00",
                        "MinValueDate": "2024-12-30T00:00:00",
                        "Values": [289.81, 290.92, 287.63],
                    },
                ],
                "TimeZoneLabel": "EST",
                "DisplaySymbol": "",
            }
        ],
    }


@pytest.mark.usefixtures("mock_ft_data_response")
def test_ft_loader__get_payload() -> None:
    """Test FTLoader.get_payload."""
    loader = FTLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )

    assert loader.get_payload() == {
        "days": 180,
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
                "Symbol": "535627197",
                "OverlayIndicators": [],
                "Params": {},
            }
        ],
    }


@pytest.mark.usefixtures("mock_ft_data_response")
def test_ft_loader__to_source_data() -> None:
    """Test FTLoader.to_source_data."""
    loader = FTLoader(
        isin_code="SE0005796331",
        lookup_key="535627197",
        name="test",
    )

    assert loader.to_source_data() == [
        SourceData(
            report_date=datetime(2024, 12, 23, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="Handelsbanken Hållbar Energi (A1 SEK)",
            price=289.81,
        ),
        SourceData(
            report_date=datetime(2024, 12, 27, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="Handelsbanken Hållbar Energi (A1 SEK)",
            price=290.92,
        ),
        SourceData(
            report_date=datetime(2024, 12, 30, 0, 0),  # noqa: DTZ001
            isin_code="SE0005796331",
            name="Handelsbanken Hållbar Energi (A1 SEK)",
            price=287.63,
        ),
    ]
