"""Tests for security_holding_history.py."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from numpy.testing import assert_array_equal
import pandas as pd
import pytest

from pypmanager.helpers.security_holding_history import (
    SecurityHoldingHistory,
    SecurityHoldingHistoryPandasAlgorithm,
)
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.conftest import DataFactory


@pytest.fixture
def mock_security_transaction_registry(
    data_factory: type[DataFactory],
) -> Generator[None]:
    """Mock the transaction registry."""
    mocked_transactions = (
        data_factory()
        .buy(transaction_date=datetime(2022, 11, 2, tzinfo=Settings.system_time_zone))
        .buy(transaction_date=datetime(2022, 11, 3, tzinfo=Settings.system_time_zone))
        .buy(transaction_date=datetime(2022, 11, 4, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2022, 12, 4, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2022, 12, 8, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2022, 12, 9, tzinfo=Settings.system_time_zone))
        .buy(transaction_date=datetime(2022, 12, 10, tzinfo=Settings.system_time_zone))
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
    shh = SecurityHoldingHistory(
        isin_code="US1234567890",
        df_transaction_registry=transaction_registry,
    )

    assert len(shh.transaction_list) == 7


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__series_date_range() -> None:
    """Test SecurityHoldingHistory.series_date_range."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory(
        isin_code="US1234567890",
        df_transaction_registry=transaction_registry,
    )

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
    shh = SecurityHoldingHistory(
        isin_code="US1234567890",
        df_transaction_registry=transaction_registry,
    )

    assert shh.df_base is not None
    assert len(shh.df_base) == 40
    assert shh.df_base.index[0] == shh.series_start_date
    assert shh.df_base.index[-1] == shh.series_end_date


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__df_base_with_transactions() -> None:
    """Test SecurityHoldingHistory.df_base_with_transactions."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory(
        isin_code="US1234567890",
        df_transaction_registry=transaction_registry,
    )

    assert shh.df_base_with_transactions is not None
    assert len(shh.df_base_with_transactions) == 40
    assert shh.df_base.index[0] == shh.series_start_date
    assert shh.df_base.index[-1] == shh.series_end_date


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__df_transaction_clean() -> None:
    """Test SecurityHoldingHistory.df_base_with_transactions."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory(
        isin_code="US1234567890",
        df_transaction_registry=transaction_registry,
    )

    assert shh.df_transaction_clean is not None
    assert len(shh.df_transaction_clean) == 40

    assert shh.df_base.index[0] == shh.series_start_date
    assert shh.df_base.index[-1] == shh.series_end_date


@pytest.mark.usefixtures("mock_security_transaction_registry")
@pytest.mark.asyncio
async def test_security_holding_history__df_transaction_filled() -> None:
    """Test SecurityHoldingHistory.df_transaction_filled."""
    transaction_registry = await TransactionRegistry().async_get_registry()
    shh = SecurityHoldingHistory(
        isin_code="US1234567890",
        df_transaction_registry=transaction_registry,
    )

    assert shh.df_transaction_filled is not None
    assert len(shh.df_transaction_filled) == 40

    actual_average_price = shh.df_transaction_filled[
        TransactionRegistryColNameValues.PRICE_PER_UNIT.value
    ].to_numpy()
    expected_average_price = [
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        0.0,
        10.0,
        10.0,
    ]
    assert_array_equal(
        actual_average_price,
        expected_average_price,
    )


@pytest.mark.parametrize(
    ("row_data", "expected"),
    [
        (
            {
                TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value: 10,
                TransactionRegistryColNameValues.PRICE_PER_UNIT.value: 100,
                TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value: False,  # noqa: E501
            },
            100.0,
        ),
        (
            {
                TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value: 0,
                TransactionRegistryColNameValues.PRICE_PER_UNIT.value: 100,
                TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value: True,  # noqa: E501
            },
            0.0,
        ),
        (
            {
                TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value: 0,
                TransactionRegistryColNameValues.PRICE_PER_UNIT.value: 100,
                TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value: False,  # noqa: E501
            },
            None,
        ),
    ],
)
def test_clean_calc_agg_sum_quantity_held(
    row_data: dict[str, Any], expected: float | None
) -> None:
    """Test SecurityHoldingHistoryPandasAlgorithm.clean_calc_agg_sum_quantity_held."""
    row = pd.Series(row_data)
    result = SecurityHoldingHistoryPandasAlgorithm.clean_calc_agg_sum_quantity_held(row)
    assert result == expected
