"""Base loader."""
from abc import abstractmethod
from typing import Any

from .models import SourceData


class BaseMarketDataLoader:
    """Base class for market data loading."""

    url: str
    raw_response: dict[str, Any]

    def __init__(self, isin_code: str, lookup_key: str) -> None:
        """Init class."""
        self.isin_code = isin_code
        self.lookup_key = lookup_key

        self.get_response()

    @abstractmethod
    def get_response(self) -> None:
        """Get reqponse."""

    @abstractmethod
    def to_source_data(self) -> list[SourceData]:
        """Convert to SourceData."""
