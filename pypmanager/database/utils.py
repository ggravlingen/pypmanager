"""Database utils."""

from __future__ import annotations

import logging
from typing import TypeVar

from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

LOGGER = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for SQLAlchemy models."""


T = TypeVar("T", bound=Base)


def check_table_exists(connection: Connection, table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(connection)
    return table_name in inspector.get_table_names()


async def async_upsert_data(*, session: AsyncSession, data_list: list[T]) -> None:
    """;erge (upsert) or insert data."""
    for item in data_list:
        try:
            await session.merge(item)  # Merge (upsert)
        except ValueError:
            LOGGER.exception("Failed to merge item")

        await session.commit()  # Commit after processing all items
