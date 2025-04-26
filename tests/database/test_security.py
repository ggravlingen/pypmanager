"""Tests for database.market_data module."""

from __future__ import annotations

import pytest

from pypmanager.database.helpers import sync_security_files_to_db
from pypmanager.database.security import AsyncDbSecurity, SecurityModel


@pytest.mark.asyncio
async def test_store_security(
    sample_security: list[SecurityModel],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test inserting data into the table."""
    async with AsyncDbSecurity() as db:
        await db.async_store_data(data=sample_security)
        assert "Committed 1 items (skipped 0)" in caplog.text


@pytest.mark.asyncio
async def test_async_get_all_data(
    sample_security: list[SecurityModel],
) -> None:
    """Test method get_market_data."""
    async with AsyncDbSecurity() as db:
        await db.async_store_data(data=sample_security)

        data = await db.async_filter_all()
        assert len(data) == 1

        assert data[0].isin_code == "US0378331005"
        assert data[0].name == "Apple Inc."
        assert data[0].currency == "USD"


@pytest.mark.asyncio
@pytest.mark.usefixtures("load_security_data")
async def test_sync_files_to_db(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test function sync_files_to_db."""
    await sync_security_files_to_db()

    assert "Committed " in caplog.text
