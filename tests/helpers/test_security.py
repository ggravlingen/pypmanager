"""Tests for security helpers."""

from __future__ import annotations

import pytest
import pytest_asyncio

from pypmanager.database.security import AsyncDbSecurity, SecurityModel
from pypmanager.helpers import (
    async_security_map_isin_to_security,
)
from pypmanager.helpers.security import async_security_map_name_to_isin


@pytest_asyncio.fixture(name="load_security_data")
async def load_security_data_fixture() -> list[dict[str, str]]:
    """Security data fixture."""
    async with AsyncDbSecurity() as db:
        await db.async_store_data(
            data=[
                SecurityModel(
                    isin_code="SE0005188836",
                    name="Länsförsäkringar Global Index",
                    currency="SEK",
                ),
            ]
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("load_security_data")
async def test_async_load_security_data() -> None:
    """Test async_load_security_data."""
    result = await async_security_map_isin_to_security()

    assert len(result) == 1
    assert result.get("SE0005188836").name == "Länsförsäkringar Global Index"
    assert result.get("SE0005188836").isin_code == "SE0005188836"
    assert result.get("SE0005188836").currency == "SEK"


@pytest.mark.asyncio
@pytest.mark.usefixtures("load_security_data")
async def test_async_security_map_name_to_isin() -> None:
    """Test function async_security_map_name_to_isin."""
    result = await async_security_map_name_to_isin()
    assert len(result) == 1
    assert result.get("Länsförsäkringar Global Index") == "SE0005188836"
