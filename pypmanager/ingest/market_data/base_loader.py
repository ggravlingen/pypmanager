"""Base loader."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from typing import TYPE_CHECKING, Any, cast

import requests

from pypmanager.const import HttpStatusCodes

if TYPE_CHECKING:
    from io import BytesIO

    from .models import SourceData


class BaseMarketDataLoader(ABC):
    """Base class for market data loading."""

    TIMEOUT_SECOND = 10

    raw_response: dict[str, Any]
    raw_response_io: BytesIO

    def __init__(
        self: BaseMarketDataLoader,
        isin_code: str,
        lookup_key: str,
        name: str | None = None,
    ) -> None:
        """Init class."""
        self.isin_code = isin_code
        self.lookup_key = lookup_key
        self.name = name

        self.get_response()

    @property
    def extra_headers(self: BaseMarketDataLoader) -> dict[str, str] | None:
        """Return headers."""
        return None

    @property
    def headers(self: BaseMarketDataLoader) -> dict[str, str]:
        """Return headers."""
        base_headers: dict[str, str] = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                "like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            )
        }
        if self.extra_headers:
            base_headers.update(self.extra_headers)

        return base_headers

    def query_endpoint(self: BaseMarketDataLoader) -> dict[str, Any]:
        """Get data endpoint."""
        response = requests.get(self.full_url, timeout=10)
        response.raise_for_status()

        if response.status_code == HttpStatusCodes.OK:
            return cast(dict[str, Any], json.loads(response.text))

        return {}

    @abstractmethod
    def get_response(self: BaseMarketDataLoader) -> None:
        """Get reqponse."""

    @property
    @abstractmethod
    def source(self: BaseMarketDataLoader) -> str:
        """Get name of source."""

    @property
    @abstractmethod
    def full_url(self: BaseMarketDataLoader) -> str:
        """Full URL to query."""

    @abstractmethod
    def to_source_data(self: BaseMarketDataLoader) -> list[SourceData]:
        """Convert to SourceData."""
