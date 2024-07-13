"""Tests for graphql."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
import pandas as pd
import pytest

from pypmanager.api import app

client = TestClient(app)


@pytest.fixture
def _mock_transaction_list(
    df_transaction_data_factory: Callable[[int], pd.DataFrame],
) -> Generator[None, Any, None]:
    """Mock the transaction list."""
    mocked_transactions = df_transaction_data_factory(no_rows=1)

    with patch(
        "pypmanager.general_ledger.helpers.load_transaction_files",
        return_value=mocked_transactions,
    ):
        yield


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list")
async def test_graphql_endpoint() -> None:
    """Test endpoint /graphql."""
    query = """
    {
        allGeneralLedger {
            transactionDate
            broker
            source
            action
            name
            noTraded
            aggBuyVolume
            averagePrice
            amount
            commission
            cashFlow
            fx
            averageFxRate
            account
            credit
            debit
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert len(response.json()["data"]["allGeneralLedger"]) == 2
