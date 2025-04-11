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
    """Merge (upsert) or insert data."""
    successful_merges = 0
    failed_merges = 0

    try:
        for item in data_list:
            try:
                await session.merge(item)  # Merge (upsert)
                successful_merges += 1
            except ValueError:
                # This is likely the NumPy array truth value error
                failed_merges += 1
                LOGGER.exception(f"Failed to merge item ({type(item).__name__})")
                continue
            except Exception:
                failed_merges += 1
                LOGGER.exception(
                    f"Unexpected error merging item ({type(item).__name__})"
                )
                continue

        # Commit once after processing all items
        if successful_merges > 0:
            await session.commit()
            LOGGER.debug(
                f"Committed {successful_merges} items (skipped {failed_merges})"
            )
        else:
            await session.rollback()
            LOGGER.warning(
                f"No successful merges to commit, all {failed_merges} items failed"
            )

    except Exception:
        # If any exception occurs, roll back the transaction
        await session.rollback()
        LOGGER.exception("Error during upsert operation")
        raise
