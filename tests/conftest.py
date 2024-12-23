"""Conftest.py file for pytest."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import PropertyMock, patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.settings import Settings, TypedSettings

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session", autouse=True)
def _mock_dir_market_data() -> Generator[Any, Any, Any]:
    """Return the path to the market data."""
    with patch.object(
        TypedSettings, "dir_market_data", new_callable=PropertyMock
    ) as mock_dir:
        mock_dir.return_value = Path("tests/fixtures/market_data").resolve()
        yield


class DataFactory:
    """Create test data."""

    transaction_list: list[dict[str, Any]]

    def __init__(self) -> None:
        """Initialize the class."""
        self.transaction_list = []

    def buy(
        self,
        transaction_date: datetime = datetime(
            2021, 1, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
        price: float = 10.0,
        commission: float = -1.0,
    ) -> DataFactory:
        """Add a buy transaction."""
        self.transaction_list.append(
            {
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: (
                    transaction_date
                ),
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value: (
                    TransactionTypeValues.BUY.value
                ),
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Company A",
                TransactionRegistryColNameValues.SOURCE_ISIN: "US1234567890",
                TransactionRegistryColNameValues.SOURCE_VOLUME.value: no_traded,
                TransactionRegistryColNameValues.SOURCE_PRICE.value: price,
                TransactionRegistryColNameValues.SOURCE_FEE.value: commission,
                TransactionRegistryColNameValues.SOURCE_CURRENCY.value: "SEK",
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker A",
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "test-file",
                TransactionRegistryColNameValues.SOURCE_ACCOUNT_NAME.value: "test",
            }
        )
        return self

    def sell(
        self,
        transaction_date: datetime = datetime(
            2021, 2, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
        price: float = 15.0,
        commission: float = -1.0,
    ) -> DataFactory:
        """Add a sell transaction."""
        self.transaction_list.append(
            {
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: (
                    transaction_date
                ),
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value: (
                    TransactionTypeValues.SELL.value
                ),
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Company A",
                TransactionRegistryColNameValues.SOURCE_ISIN: "US1234567890",
                TransactionRegistryColNameValues.SOURCE_VOLUME.value: no_traded,
                TransactionRegistryColNameValues.SOURCE_PRICE.value: price,
                TransactionRegistryColNameValues.SOURCE_FEE.value: commission,
                TransactionRegistryColNameValues.SOURCE_CURRENCY.value: "SEK",
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker A",
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "test-file",
                TransactionRegistryColNameValues.SOURCE_ACCOUNT_NAME.value: "test",
            }
        )
        return self

    def dividend(
        self,
        transaction_date: datetime = datetime(
            2021, 2, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
        price: float = 15.0,
    ) -> DataFactory:
        """Add a sell transaction."""
        self.transaction_list.append(
            {
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: (
                    transaction_date
                ),
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value: (
                    TransactionTypeValues.DIVIDEND.value
                ),
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Company A",
                TransactionRegistryColNameValues.SOURCE_ISIN: "US1234567890",
                TransactionRegistryColNameValues.SOURCE_VOLUME.value: no_traded,
                TransactionRegistryColNameValues.SOURCE_PRICE.value: price,
                TransactionRegistryColNameValues.SOURCE_CURRENCY.value: "SEK",
                TransactionRegistryColNameValues.SOURCE_BROKER.value: "Broker A",
                TransactionRegistryColNameValues.SOURCE_FX.value: 1.0,
                TransactionRegistryColNameValues.SOURCE_FILE.value: "test-file",
            }
        )
        return self

    @property
    def df_transaction_list(self) -> pd.DataFrame:
        """Return the transaction list as a DataFrame."""
        return pd.DataFrame(self.transaction_list)


@pytest.fixture(name="data_factory", scope="session")
def data_factory() -> DataFactory:
    """Return a factory to mock transaction data."""
    return DataFactory


class MarketDataFactory:
    """Create test market data."""

    market_data_list: list[dict[str, Any]]

    def __init__(self: MarketDataFactory) -> None:
        """Initialize the class."""
        self.market_data_list = []

    def add(
        self: MarketDataFactory,
        *,
        isin_code: str,
        report_date: date,
        price: float = 10.0,
    ) -> MarketDataFactory:
        """Add a buy transaction."""
        self.market_data_list.append(
            {
                "isin_code": isin_code,
                "name": "Test",
                "report_date": report_date,
                "price": price,
                "date_added_utc": datetime.now(tz=UTC),
                "source": "test",
            }
        )
        return self

    @property
    def df_market_data_list(self: MarketDataFactory) -> pd.DataFrame:
        """Return the market data list as a DataFrame."""
        return pd.DataFrame(self.market_data_list).set_index("report_date")


@pytest.fixture(name="market_data_factory", scope="session")
def market_data_factory() -> MarketDataFactory:
    """Return a factory to mock transaction data."""
    return MarketDataFactory
