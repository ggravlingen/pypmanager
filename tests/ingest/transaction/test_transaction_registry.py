"""Test helpers."""

from datetime import datetime
from unittest.mock import patch

import pytest

from pypmanager.ingest.transaction import TransactionRegistry
from pypmanager.settings import Settings

from tests.conftest import DataFactory


@pytest.mark.asyncio()
async def test_transaction_registry(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_aggregate_ledger_by_year."""
    factory = data_factory()
    mocked_transactions = factory.buy().sell().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        registry = await TransactionRegistry().async_get_registry()
        assert len(registry) == 2


@pytest.mark.asyncio()
async def test_transaction_registry__date_filter(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_aggregate_ledger_by_year."""
    factory = data_factory()
    mocked_transactions = factory.buy().sell().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        registry = await TransactionRegistry(
            report_date=datetime(2021, 1, 15, tzinfo=Settings.system_time_zone)
        ).async_get_registry()
        assert len(registry) == 1


@pytest.mark.asyncio()
async def test_transaction_registry__date_filter__raises(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_aggregate_ledger_by_year."""
    factory = data_factory()
    mocked_transactions = factory.buy().sell().df_transaction_list
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
        pytest.raises(ValueError, match="report_date argument must be time zone aware"),
    ):
        await TransactionRegistry(
            report_date=datetime(2021, 1, 15)  # noqa: DTZ001
        ).async_get_registry()
