"""Tests for security_holding_history.py."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from pypmanager.helpers.security_holding_history import SecurityHoldingHistory
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.conftest import DataFactory


@pytest.fixture
def mock_security_transaction_registry(
    data_factory: type[DataFactory],
) -> Generator[None, None, None]:
    """Mock the transaction registry."""
    mocked_transactions = (
        data_factory()
        .buy(transaction_date=datetime(2022, 11, 2, tzinfo=Settings.system_time_zone))
        .buy(transaction_date=datetime(2022, 11, 3, tzinfo=Settings.system_time_zone))
        .buy(transaction_date=datetime(2022, 11, 4, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2022, 12, 8, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2022, 12, 9, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2022, 12, 10, tzinfo=Settings.system_time_zone))
        .df_transaction_list
    )
    with patch(
        "pypmanager.helpers.chart.TransactionRegistry._load_transaction_files",
        return_value=mocked_transactions,
    ):
        yield


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__transaction_list() -> None:
    """Test SecurityHoldingHistory.series_date_range."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory("US1234567890", transaction_registry)

    assert len(shh.transaction_list) == 6


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__series_date_range() -> None:
    """Test SecurityHoldingHistory.series_date_range."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory("US1234567890", transaction_registry)

    # Test the series_date_range property
    assert shh.series_date_range is not None
    assert len(shh.series_date_range) == 40
    assert shh.series_date_range[0] == shh.series_start_date
    assert shh.series_date_range[-1] == shh.series_end_date


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__df_base() -> None:
    """Test SecurityHoldingHistory.df_base."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory("US1234567890", transaction_registry)

    assert shh.df_base is not None
    assert len(shh.df_base) == 40
    assert shh.df_base.index[0] == shh.series_start_date
    assert shh.df_base.index[-1] == shh.series_end_date


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__df_base_with_transactions() -> None:
    """Test SecurityHoldingHistory.df_base_with_transactions."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory("US1234567890", transaction_registry)

    assert shh.df_base_with_transactions is not None
    assert len(shh.df_base_with_transactions) == 40
    assert shh.df_base.index[0] == shh.series_start_date
    assert shh.df_base.index[-1] == shh.series_end_date


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__df_transaction_clean() -> None:
    """Test SecurityHoldingHistory.df_base_with_transactions."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory("US1234567890", transaction_registry)

    assert shh.df_transaction_clean is not None
    assert len(shh.df_transaction_clean) == 40

    assert shh.df_base.index[0] == shh.series_start_date
    assert shh.df_base.index[-1] == shh.series_end_date
