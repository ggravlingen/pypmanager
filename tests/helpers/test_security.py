"""Tests for security helpers."""

from __future__ import annotations

import pytest

from pypmanager.helpers.security import async_security_map_isin_to_security


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_load_security_data() -> None:
    """Test async_load_security_data."""
    result = await async_security_map_isin_to_security()

    assert len(result) == 2
    assert result.get("SE0005188836").name == "Länsförsäkringar Global Index"
    assert result.get("SE0005188836").isin_code == "SE0005188836"
    assert result.get("SE0005188836").currency == "SEK"
