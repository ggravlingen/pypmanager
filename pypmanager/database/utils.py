"""Database utils."""

from __future__ import annotations

from sqlalchemy import Connection, inspect


def check_table_exists(connection: Connection, table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(connection)
    return table_name in inspector.get_table_names()
