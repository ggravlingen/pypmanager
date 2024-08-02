"""Tests for graphql."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

from pypmanager.api import app

if TYPE_CHECKING:
    from collections.abc import Generator

    from freezegun.api import FrozenDateTimeFactory

    from tests.conftest import DataFactory

client = TestClient(app)


@pytest.fixture(scope="module")
def _mock_transaction_list_graphql(
    data_factory: type[DataFactory],
) -> Generator[Any, Any, Any]:
    """Mock transaction list."""
    factory = data_factory()
    mocked_transactions = factory.buy().sell().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        yield


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
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
    assert len(response.json()["data"]["allGeneralLedger"]) == 6


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
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
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
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
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
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
            currency
            price
            commission
            fx
            cashFlow
            costBaseAverage
            quantityHeld
            pnlTotal
            pnlTrade
            pnlDividend
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert len(response.json()["data"]["allTransaction"]) == 2


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
async def test_graphql_query__result_statement() -> None:
    """Test query resultStatement."""
    query = """
    {
        resultStatement {
            itemName
            yearList
            amountList
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert len(response.json()["data"]["resultStatement"]) == 1
