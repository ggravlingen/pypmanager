"""Test market data helpers."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import PropertyMock, patch

import pytest

from pypmanager.helpers.market_data import (
    _class_importer,
    async_get_market_data_overview,
    async_load_market_data_config,
    get_market_data,
)
from pypmanager.settings import Settings, TypedSettings

if TYPE_CHECKING:
    from tests.conftest import MarketDataFactory


@pytest.mark.asyncio
async def test_async_load_market_data_config() -> None:
    """Test async_load_market_data_config."""
    with patch.object(
        TypedSettings,
        "file_market_data_config_local",
        new_callable=PropertyMock,
    ) as mock_file_market_data_config_local:
        mock_file_market_data_config_local.return_value = (
            Settings.dir_config / "market_data.yaml"
        )

        result = await async_load_market_data_config()

        assert len(result) == 6


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
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_get_market_data_overview(
    market_data_factory: type[MarketDataFactory],
) -> None:
    """Test async_get_market_data_overview."""
    mocked_market_data = (
        market_data_factory().add(
            isin_code="SE0003788587", report_date=date(2022, 11, 1), price=100.0
        )
    ).df_market_data_list

    with (
        patch.object(
            TypedSettings, "file_market_data_config_local", new_callable=PropertyMock
        ) as mock_file_market_data_config_local,
        patch(
            "pypmanager.helpers.market_data.get_market_data",
            return_value=mocked_market_data,
        ),
    ):
        mock_file_market_data_config_local.return_value = Path("foo.yaml")

        result = await async_get_market_data_overview()

        assert len(result) == 3
        assert result[0].isin_code == "SE0003788587"
        assert result[0].name is None
        assert result[0].first_date == date(2022, 11, 1)
        assert result[0].last_date == date(2022, 11, 1)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_get_market_data_overview__missing_data() -> None:
    """Test async_get_market_data_overview with missing data."""
    with (
        patch.object(
            TypedSettings, "file_market_data_config_local", new_callable=PropertyMock
        ) as mock_file_market_data_config_local,
    ):
        mock_file_market_data_config_local.return_value = Path("foo.yaml")

        result = await async_get_market_data_overview()

        assert len(result) == 3
        assert result[0].isin_code == "SE0003788587"
        assert result[0].name is None
        assert result[0].first_date is None
        assert result[0].last_date is None


def test_class_importer() -> None:
    """Test function _class_importer."""
    class_name = "datetime.datetime"  # Define a fully qualified class name

    # Use the _class_importer function to load the class
    loaded_class = _class_importer(class_name)

    # Verify that the loaded class is the correct class
    assert loaded_class == datetime

    # Verify that an instance of the loaded class can be created
    instance = loaded_class(2023, 1, 1)
    assert isinstance(instance, datetime) is True
