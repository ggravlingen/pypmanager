"""Tests for graphql."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from freezegun import freeze_time
import pytest

from pypmanager.api import app
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.conftest import DataFactory, MarketDataFactory

client = TestClient(app)


@pytest.fixture(scope="module")
def _mock_transaction_list_graphql(
    data_factory: type[DataFactory],
) -> Generator[Any, Any, Any]:
    """Mock transaction list."""
    factory = data_factory()
    mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2022, 11, 1, tzinfo=Settings.system_time_zone)
        )
        .sell(transaction_date=datetime(2022, 11, 2, tzinfo=Settings.system_time_zone))
        .df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        yield


@pytest.fixture(scope="module")
def _mock_market_data_graphql(
    market_data_factory: type[MarketDataFactory],
) -> Generator[Any, Any, Any]:
    """Mock market data."""
    mocked_market_data = (
        market_data_factory()
        .add(isin_code="US1234567890", report_date=date(2022, 11, 1), price=100.0)
        .add(
            isin_code="US1234567890",
            report_date=date(2022, 11, 2),
            price=90.0,
        )
    ).df_market_data_list
    with (
        patch(
            "pypmanager.helpers.chart.get_market_data",
            return_value=mocked_market_data,
        ),
    ):
        yield


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
@freeze_time(date(2022, 12, 5))
async def test_graphql_query__historical_portfolio() -> None:
    """Test query historicalPortfolio."""
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
    assert len(response.json()["data"]["historicalPortfolio"]) == 1


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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
    assert len(response.json()["data"]["resultStatement"]) == 3


@pytest.mark.asyncio
@pytest.mark.usefixtures("_mock_transaction_list_graphql")
@pytest.mark.usefixtures("_mock_market_data_graphql")
async def test_graphql_query__chart_history() -> None:
    """Test query chartHistory."""
    query = """
    query ($isinCode: String!, $startDate: String!, $endDate: String!) {
        chartHistory(isinCode: $isinCode, startDate: $startDate, endDate: $endDate) {
            yVal
            xVal
            volumeBuy
            volumeSell
        }
    }
    """
    variables = {
        "isinCode": "US1234567890",
        "startDate": "2022-11-01",
        "endDate": "2022-11-30",
    }
    response = client.post("/graphql", json={"query": query, "variables": variables})

    assert response.status_code == 200
    assert len(response.json()["data"]["chartHistory"]) == 22
