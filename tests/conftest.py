"""Conftest.py file for pytest."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import PropertyMock, patch

import pandas as pd
import pytest
import pytest_asyncio

from pypmanager.database.daily_portfolio_holding import (
    AsyncDbDailyPortfolioHolding,
    DailyPortfolioMoldingModel,
)
from pypmanager.database.market_data import AsyncMarketDataDB, MarketDataModel
from pypmanager.database.security import AsyncDbSecurity, SecurityModel
from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.settings import Settings, TypedSettings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

DB_NAME_TEST = "test_database.sqllite"


@pytest.fixture(scope="session", autouse=True)
def mock_db_file_location() -> Generator[Any, Any, Any]:
    """
    Fixture for mocking location of database.

    Deleted after each test.

    Maybe purge table instead?
    """
    db_path = Path("tests") / DB_NAME_TEST

    with patch.object(
        TypedSettings,
        "database_local",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = db_path

        yield

        # Cleanup after tests
        db_path.unlink(missing_ok=True)


@pytest_asyncio.fixture(autouse=True)
async def async_cleanup_db() -> AsyncGenerator[None]:
    """Cleanup table after each test."""
    yield
    async with AsyncMarketDataDB() as db:
        await db._async_purge_table()  # pylint: disable=protected-access # noqa: SLF001

    async with AsyncDbDailyPortfolioHolding() as db:
        await db._async_purge_table()  # pylint: disable=protected-access # noqa: SLF001

    async with AsyncDbSecurity() as db:
        await db._async_purge_table()  # pylint: disable=protected-access # noqa: SLF001


@pytest.fixture(name="sample_market_data")
def sample_market_data_fixture() -> list[MarketDataModel]:
    """Fixture providing sample market data for testing."""
    return [
        MarketDataModel(
            isin_code="US0378331005",  # Apple
            report_date=date(2023, 1, 1),
            close_price=150.25,
            currency=None,
            date_added=date(2023, 1, 2),
            source="test",
        ),
        MarketDataModel(
            isin_code="US0231351067",  # Amazon
            report_date=date(2023, 1, 1),
            close_price=102.75,
            currency=None,
            date_added=date(2023, 1, 2),
            source="test",
        ),
    ]


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


@pytest.fixture(name="sample_daily_portfolio_holding")
def sample_daily_portfolio_holding_fixture() -> list[DailyPortfolioMoldingModel]:
    """Fixture providing sample data for a daily portfolio holding."""
    return [
        DailyPortfolioMoldingModel(
            isin_code="US0378331005",
            report_date=date(2023, 1, 1),
            no_held=10.0,
        ),
    ]


@pytest.fixture(name="sample_security", autouse=True)
def sample_security_fixture() -> list[SecurityModel]:
    """Sample fixture for security data."""
    return [
        SecurityModel(isin_code="US0378331005", name="Apple Inc.", currency="USD"),
    ]


@pytest.fixture
def mock_file_security_config_local() -> Generator[Any, Any, Any]:
    """
    Mock the local security config file.

    The purpose of doing this is to avoid loading the local data during tests.
    """
    with patch.object(
        TypedSettings, "security_config_local", new_callable=PropertyMock
    ) as mock:
        mock.return_value = Settings.security_config
        yield


@pytest.fixture(scope="session", autouse=True)
def _mock_dir_market_data() -> Generator[Any, Any, Any]:
    """Return the path to the market data."""
    with patch.object(
        TypedSettings, "dir_market_data_local", new_callable=PropertyMock
    ) as mock_dir:
        mock_dir.return_value = Path("tests/fixtures/market_data").resolve()
        yield


class DataFactory:
    """Create test data."""

    transaction_list: list[dict[str, Any]]

    def __init__(self) -> None:
        """Initialize the class."""
        self.transaction_list = []

    def buy(  # noqa: PLR0913
        self,
        name: str = "Company A",
        transaction_date: datetime = datetime(
            2021, 1, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
        price: float = 10.0,
        commission: float = -1.0,
        isin_code: str = "US1234567890",
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
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: name,
                TransactionRegistryColNameValues.SOURCE_ISIN: isin_code,
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

    def sell(  # noqa: PLR0913
        self,
        name: str = "Company A",
        transaction_date: datetime = datetime(
            2021, 2, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
        price: float = 15.0,
        commission: float = -1.0,
        isin_code: str = "US1234567890",
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
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: name,
                TransactionRegistryColNameValues.SOURCE_ISIN: isin_code,
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
        name: str = "Company A",
        transaction_date: datetime = datetime(
            2021, 2, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
        price: float = 15.0,
        isin_code: str = "US1234567890",
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
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: name,
                TransactionRegistryColNameValues.SOURCE_ISIN: isin_code,
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
        """Add a market data entry."""
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
