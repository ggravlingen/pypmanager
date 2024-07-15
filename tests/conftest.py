"""Conftest.py file for pytest."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import TransactionTypeValues


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
