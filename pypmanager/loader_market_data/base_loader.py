"""Base loader."""
from abc import abstractmethod
from io import BytesIO
import json
from typing import Any, cast

import requests

from pypmanager.const import HttpResponseCodeLabels

from .models import SourceData


class BaseMarketDataLoader:
    """Base class for market data loading."""

    raw_response: dict[str, Any]
    raw_response_io: BytesIO

    def __init__(
        self,
        isin_code: str,
        lookup_key: str,
        name: str | None = None,
    ) -> None:
        """Init class."""
        self.isin_code = isin_code
        self.lookup_key = lookup_key
        self.name = name

        self.get_response()

    def query_endpoint(self) -> dict[str, Any]:
        """Get data endpoint."""
        response = requests.get(self.full_url, timeout=10)

        if response.status_code == HttpResponseCodeLabels.OK:
            return cast(dict[str, Any], json.loads(response.text))

        raise ValueError("Unable to load data")

    @abstractmethod
    def get_response(self) -> None:
        """Get reqponse."""

    @property
    @abstractmethod
    def source(self) -> str:
        """Get name of source."""

    @property
    @abstractmethod
    def full_url(self) -> str:
        """Full URL to query."""

    @abstractmethod
    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
