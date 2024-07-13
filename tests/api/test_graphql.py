"""Tests for graphql."""

from collections.abc import Callable, Generator
from datetime import date
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from freezegun.api import FrozenDateTimeFactory
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


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list")
async def test_graphql_query__all_general_ledger() -> None:
    """Test query allGeneralLedger."""
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


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list")
async def test_graphql_query__current_portfolio() -> None:
    """Test query currentPortfolio."""
    query = """
    {
        currentPortfolio {
            name
            dateMarketValue
            investedAmount
            marketValue
            currentHoldings
            currentPrice
            averagePrice
            returnPct
            totalPnl
            realizedPnl
            unrealizedPnl
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list")
async def test_graphql_query__historical_portfolio(
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test query historicalPortfolio."""
    freezer.move_to(date(2023, 8, 5))

    query = """
    {
        historicalPortfolio {
            reportDate
            investedAmount
            marketValue
            returnPct
            realizedPnl
            unrealizedPnl
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert len(response.json()["data"]["historicalPortfolio"]) == 9


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list")
async def test_graphql_query__all_transaction() -> None:
    """Test query allTransaction."""
    query = """
    {
        allTransaction {
            transactionDate
            broker
            source
            action
            name
            noTraded
            price
            commission
            fx
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert len(response.json()["data"]["allTransaction"]) == 1
