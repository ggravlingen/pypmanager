"""Conftest.py file for pytest."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import PropertyMock, patch

import numpy as np
import pandas as pd
import pytest

from pypmanager.ingest.transaction.base_loader import (
    _normalize_amount,
    _normalize_fx,
    _normalize_no_traded,
)
from pypmanager.ingest.transaction.const import ColumnNameValues, TransactionTypeValues
from pypmanager.settings import Settings, TypedSettings

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


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

    def buy(self) -> DataFactory:
        """Add a buy transaction."""
        self.transaction_list.append(
            {
                "transaction_date": datetime(
                    2021, 1, 1, tzinfo=Settings.system_time_zone
                ),
                "transaction_type": TransactionTypeValues.BUY.value,
                "name": "Company A",
                "isin_code": "US1234567890",
                "no_traded": 10.0,
                "price": 10.0,
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
        df_data = pd.DataFrame(self.transaction_list)
        df_data[ColumnNameValues.NO_TRADED] = df_data.apply(
            _normalize_no_traded, axis=1
        )
        df_data[ColumnNameValues.AMOUNT] = df_data.apply(_normalize_amount, axis=1)
        df_data[ColumnNameValues.FX] = df_data.apply(_normalize_fx, axis=1)

        # Make the transaction_date field into the index
        df_data.index = df_data["transaction_date"]

        # Drop field transaction_date
        return df_data.drop(columns=["transaction_date"])


@pytest.fixture(name="data_factory", scope="session")
def data_factory() -> type[DataFactory]:
    """Return a factory to mock transaction data."""
    return DataFactory()


@pytest.fixture(name="df_transaction_data_factory", scope="session")
def transaction_data_factory() -> Callable[[int], pd.DataFrame]:
    """Return a factory function for generating test data."""

    def fixture_function(no_rows: int) -> pd.DataFrame:
        """Generate test data."""
        rng = np.random.default_rng()

        # Define start and end dates for the date range
        start_date = "2021-01-01"
        end_date = "2021-12-31"

        # Generate a date range
        date_range = pd.date_range(start=start_date, end=end_date)

        random_dates = rng.choice(date_range, size=no_rows, replace=True)

        data = {
            "transaction_date": random_dates,
            "transaction_type": rng.choice(
                [TransactionTypeValues.BUY.value, TransactionTypeValues.SELL.value],
                size=no_rows,
            ),
            "name": rng.choice(["Company A", "Company B", "Company C"], size=no_rows),
            "isin_code": rng.choice(
                ["US1234567890", "GB0987654321", "JP1234567890"], size=no_rows
            ),
            "no_traded": rng.integers(1, 1000, size=no_rows),
            "price": rng.uniform(10, 500, size=no_rows),
            "commission": 0,
            "currency": rng.choice(["SEK", "EUR"], size=no_rows),
            "broker": rng.choice(["Broker A", "Broker B"], size=no_rows),
            "source": rng.choice(["Avanza", "Lysa"], size=no_rows),
            "fx_rate": 1.0,  # Assuming this is constant for all rows
            "ledger_account": rng.choice(["Account A"], size=no_rows),
        }

        df_test_data = pd.DataFrame(data)

        df_test_data["amount"] = df_test_data["price"] * df_test_data["no_traded"]

        return df_test_data

    return fixture_function


@pytest.fixture
def _mock_transactions_general_ledger(
    df_transaction_data_factory: Callable[[int], pd.DataFrame],
) -> Generator[None, Any, None]:
    """Mock the transaction list."""
    mocked_transactions = df_transaction_data_factory(no_rows=10)

    # make the transaction_date field into the index
    mocked_transactions.index = mocked_transactions["transaction_date"]

    with (
        patch(
            "pypmanager.general_ledger.helpers.load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        yield


@pytest.fixture
def _mock_transaction_list(
    df_transaction_data_factory: Callable[[int], pd.DataFrame],
) -> Generator[None, Any, None]:
    """Mock the transaction list."""
    mocked_transactions = df_transaction_data_factory(no_rows=1)

    # make the transaction_date field into the index
    mocked_transactions.index = mocked_transactions["transaction_date"]

    with (
        patch(
            "pypmanager.general_ledger.helpers.load_transaction_files",
            return_value=mocked_transactions,
        ),
        patch(
            "pypmanager.api.graphql.query.load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        yield
