"""Tests for security helpers."""

from __future__ import annotations

import pytest

from pypmanager.helpers.security import async_load_security_data


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_load_security_data() -> None:
    """Test async_load_security_data."""
    result = await async_load_security_data()

    assert len(result) == 2
    assert result["SE0005188836"].name == "Länsförsäkringar Global Index"
    assert result["SE0005188836"].isin_code == "SE0005188836"
    assert result["SE0005188836"].currency == "SEK"
