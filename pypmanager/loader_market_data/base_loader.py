"""Base loader."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from typing import TYPE_CHECKING, Any, cast

import requests

from .const import HttpResponseCodeLabels

if TYPE_CHECKING:
    from io import BytesIO

    from .models import SourceData


class BaseMarketDataLoader(ABC):
    """Base class for market data loading."""

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

    def query_endpoint(self: BaseMarketDataLoader) -> dict[str, Any]:
        """Get data endpoint."""
        response = requests.get(self.full_url, timeout=10)

        if response.status_code == HttpResponseCodeLabels.OK:
            return cast(dict[str, Any], json.loads(response.text))

        msg = "Unable to load data"
        raise ValueError(msg)

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
