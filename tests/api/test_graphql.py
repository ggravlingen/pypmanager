"""Tests for graphql."""

from datetime import date

from fastapi.testclient import TestClient
from freezegun.api import FrozenDateTimeFactory
import pytest

from pypmanager.api import app

client = TestClient(app)


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


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transactions_general_ledger")
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
