"""Test market data helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd
import pytest

from pypmanager.database.market_data import AsyncMarketDataDB, MarketDataModel
from pypmanager.helpers.market_data import (
    _class_importer,
    async_get_last_market_data_df,
    async_get_market_data_overview,
    async_load_market_data_config,
)
from pypmanager.ingest.market_data.models import SourceData
from pypmanager.settings import Settings, TypedSettings

if TYPE_CHECKING:
    from collections.abc import Generator


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


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_security_config_local")
async def test_async_get_market_data_overview() -> None:
    """Test async_get_market_data_overview."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(
            data=[
                MarketDataModel(
                    isin_code="SE0000671919",
                    report_date=date(2022, 11, 1),
                    close_price=100.0,
                    date_added=datetime(2022, 11, 1, tzinfo=UTC),
                    source="testabc",
                )
            ]
        )

    with (
        patch.object(
            TypedSettings, "file_market_data_config_local", new_callable=PropertyMock
        ) as mock_file_market_data_config_local,
    ):
        mock_file_market_data_config_local.return_value = Path("foo.yaml")

        result = await async_get_market_data_overview()

        assert len(result) == 3
        assert result[2].isin_code == "SE0000671919"
        assert result[2].name == "Storebrand Global All Countries A SEK"
        assert result[2].first_date == date(2022, 11, 1)
        assert result[2].last_date == date(2022, 11, 1)


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


def test_class_importer_module_not_found() -> None:
    """Test function _class_importer with a non-existent module."""
    class_name = "nonexistent.module.ClassName"

    # Use the _class_importer function to load the class
    loaded_class = _class_importer(class_name)

    # Verify that the loaded class is None
    assert loaded_class is None


def test_class_importer_class_not_found() -> None:
    """Test function _class_importer with a non-existent class."""
    class_name = "datetime.NonExistentClass"

    # Use the _class_importer function to load the class
    loaded_class = _class_importer(class_name)

    # Verify that the loaded class is None
    assert loaded_class is None


@pytest.mark.asyncio
async def test_async_get_last_market_data_df(
    sample_market_data: list[MarketDataModel],
) -> None:
    """Test function async_get_last_market_data_df."""
    async with AsyncMarketDataDB() as db:
        await db.async_store_market_data(data=sample_market_data)

    result = await async_get_last_market_data_df()
    assert len(result) == 2
    assert result.iloc[0].isin_code == "US0231351067"
    assert result.iloc[0].price == 102.75

    assert result.iloc[1].isin_code == "US0378331005"
    assert result.iloc[1].price == 150.25


@pytest.fixture(name="mock_source_data")
def _mock_source_data() -> list[SourceData]:
    """Mock source data."""
    return [
        SourceData(
            isin_code="US1234567890",
            price=100.0,
            report_date=datetime(2022, 1, 1, tzinfo=UTC),
            name="Test Security",
        ),
        SourceData(
            isin_code="US1234567891",
            price=200.0,
            report_date=datetime(2022, 1, 2, tzinfo=UTC),
            name="Another Security",
        ),
    ]


@pytest.fixture(name="mock_dont_save_csv")
def _mock_dont_save_csv() -> Generator[MagicMock]:
    """Mock to_csv so we don't save to disk."""
    mock = MagicMock()
    with patch.object(pd.DataFrame, "to_csv", mock):
        yield mock
