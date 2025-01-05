"""Tests for security helpers."""

from __future__ import annotations

import pytest

from pypmanager.helpers import (
    async_security_map_isin_to_security,
)
from pypmanager.helpers.security import async_security_map_name_to_isin


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_load_security_data() -> None:
    """Test async_load_security_data."""
    result = await async_security_map_isin_to_security()

    assert len(result) == 2
    assert result.get("SE0005188836").name == "Länsförsäkringar Global Index"
    assert result.get("SE0005188836").isin_code == "SE0005188836"
    assert result.get("SE0005188836").currency == "SEK"


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_security_map_name_to_isin() -> None:
    """Test function async_security_map_name_to_isin."""
    result = await async_security_map_name_to_isin()
    assert len(result) == 2
    assert result.get("Länsförsäkringar Global Index") == "SE0005188836"
