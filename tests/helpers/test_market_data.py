"""Test market data helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from pypmanager.helpers.market_data import (
    async_get_market_data_overview,
    async_load_market_data_config,
    get_market_data,
)
from pypmanager.settings import TypedSettings


@pytest.mark.asyncio
async def test_async_load_market_data_config() -> None:
    """Test async_load_market_data_config."""
    with patch.object(
        TypedSettings, "file_market_data_config_local", new_callable=PropertyMock
    ) as mock_file_market_data_config_local:
        # Disable local market data config
        mock_file_market_data_config_local.return_value = (
            TypedSettings.dir_config / "market_data.yaml"
        )

        result = await async_load_market_data_config()

        assert len(result) == 3


def test_get_market_data() -> None:
    """Test async_get_market_data."""
    with patch.object(
        TypedSettings, "file_market_data_config_local", new_callable=PropertyMock
    ) as mock_file_market_data_config_local:
        # Disable local market data config
        mock_file_market_data_config_local.return_value = Path("foo.yaml")

        result = get_market_data()

        assert result is not None
        assert len(result) == 1
        assert result.iloc[0].isin_code == "LU0051755006"


def test_get_market_data__filter() -> None:
    """Test async_get_market_data with filter."""
    result = get_market_data(isin_code="LU0051755006")

    assert result is not None
    assert len(result) == 1
    assert result.iloc[0].isin_code == "LU0051755006"


@pytest.mark.asyncio
async def test_async_get_market_data_overview() -> None:
    """Test async_get_market_data_overview."""
    with patch.object(
        TypedSettings, "file_market_data_config_local", new_callable=PropertyMock
    ) as mock_file_market_data_config_local:
        # Disable local market data config
        mock_file_market_data_config_local.return_value = Path("foo.yaml")

        result = await async_get_market_data_overview()

        assert len(result) == 3
