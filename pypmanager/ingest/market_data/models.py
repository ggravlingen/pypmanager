"""Data models."""

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


@dataclass
class SourceData:
    """Represent source data."""

    report_date: datetime
    isin_code: str
    name: str
    price: float


class Source(BaseModel):
    """A source."""

    isin_code: str
    loader_class: str
    lookup_key: str | None = None
    name: str | None = None


class Sources(BaseModel):
    """Definition of sources."""

    sources: list[Source]
