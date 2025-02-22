"""Tests for ingest.market_data.base_loader."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest

from pypmanager.const import HttpStatusCodes
from pypmanager.ingest.market_data.base_loader import BaseMarketDataLoader

if TYPE_CHECKING:
    from pypmanager.ingest.market_data.models import SourceData


class MockMarketDataLoader(BaseMarketDataLoader):
    """Mock implementation of BaseMarketDataLoader for testing."""

    @property
    def source(self) -> str:
        """Get name of source."""
        return "mock_source"

    @property
    def full_url(self) -> str:
        """Return full URL."""
        return "http://mockurl.com"

    def get_response(self) -> None:
        """Get response."""

    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
        return []


def test_extra_headers() -> None:
    """Test the extra_headers property."""
    loader = MockMarketDataLoader(isin_code="test", lookup_key="test")

    assert loader.extra_headers is None


@pytest.mark.parametrize(
    ("status_code", "response_text", "expected_result"),
    [
        (HttpStatusCodes.OK, '{"key": "value"}', {"key": "value"}),
        (HttpStatusCodes.INTERNAL_SERVER_ERROR, "", {}),
    ],
)
def test_query_endpoint(
    status_code: int, response_text: str, expected_result: dict[str, Any]
) -> None:
    """Test the query_endpoint method."""
    loader = MockMarketDataLoader(isin_code="test", lookup_key="test")

    with patch(
        "pypmanager.ingest.market_data.base_loader.requests.Session.get"
    ) as mock_get:
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = response_text
        mock_get.return_value = mock_response

        result = loader.query_endpoint()
        assert result == expected_result
