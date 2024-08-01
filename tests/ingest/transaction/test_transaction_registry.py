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
    mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        )
        .buy(transaction_date=datetime(2021, 1, 15, tzinfo=Settings.system_time_zone))
        .sell()
        .df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        registry = await TransactionRegistry().async_get_registry()
        assert len(registry) == 3


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


@pytest.mark.asyncio()
async def test_transaction_registry__columns(
    data_factory: type[DataFactory],
) -> None:
    """Test the column names of the transaction registry."""
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
        assert registry.columns.to_list() == [
            "source_name",
            "source_transaction_type",
            "source_isin_code",
            "source_volume",
            "source_price",
            "source_fee",
            "source_currency",
            "source_broker",
            "source_fx_rate",
            "source_file_name",
            "amount",
            "calc_agg_sum_quantity_held",
            "calc_avg_price_per_unit",
            "calc_cf_net_fee_nominal_ccy",
            "calc_cf_gross_fee_nominal_ccy",
            "meta_transaction_year",
        ]
