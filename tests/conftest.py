"""Conftest.py file for pytest."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import PropertyMock, patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import TransactionTypeValues
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
    """
    Create test data.

    A transaction is represented by these columns:
    - transaction_date
    - transaction_type
    - name
    - isin_code
    - no_traded
    - price
    - amount
    - commission
    - currency
    - fx
    - broker
    """

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
    ) -> DataFactory:
        """Add a buy transaction."""
        self.transaction_list.append(
            {
                "transaction_date": transaction_date,
                "transaction_type": TransactionTypeValues.BUY.value,
                "name": "Company A",
                "isin_code": "US1234567890",
                "no_traded": no_traded,
                "price": price,
                "commission": 0.0,
                "currency": "SEK",
                "broker": "Broker A",
                "fx": 1.0,
                "source": "Test data",
            }
        )
        return self

    def sell(
        self,
        transaction_date: datetime = datetime(
            2021, 2, 1, tzinfo=Settings.system_time_zone
        ),
        no_traded: float = 10.0,
    ) -> DataFactory:
        """Add a sell transaction."""
        self.transaction_list.append(
            {
                "transaction_date": transaction_date,
                "transaction_type": TransactionTypeValues.SELL.value,
                "name": "Company A",
                "isin_code": "US1234567890",
                "no_traded": no_traded,
                "price": 15.0,
                "commission": 0.0,
                "currency": "SEK",
                "broker": "Broker A",
                "fx": 1.0,
                "source": "Test data",
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
