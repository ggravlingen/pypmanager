"""Tests for security helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from pypmanager.helpers.security import async_load_security_data
from pypmanager.settings import TypedSettings


@pytest.mark.asyncio
async def test_async_load_security_data() -> None:
    """Test async_load_security_data."""
    with patch.object(
        TypedSettings, "security_config_local", new_callable=PropertyMock
    ) as mock_file_security_config_local:
        # Disable local market data config
        mock_file_security_config_local.return_value = Path("foo.yaml")
        result = await async_load_security_data()

        assert len(result) == 1
        assert result["SE0005188836"].name == "Länsförsäkringar Global Index"
