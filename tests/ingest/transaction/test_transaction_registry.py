"""Test helpers."""

from datetime import datetime
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_array_equal
import pytest

from pypmanager.ingest.transaction import TransactionRegistry
from pypmanager.ingest.transaction.const import (
    ColumnNameValues,
    TransactionRegistryColNameValues,
)
from pypmanager.settings import Settings

from tests.conftest import DataFactory


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_transaction_registry__async_get_current_holding(
    data_factory: type[DataFactory],
) -> None:
    """Test function async_get_current_holding."""
    factory = data_factory()
    mocked_transactions = (
        # US1234567890
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        )
        .buy(transaction_date=datetime(2021, 1, 2, tzinfo=Settings.system_time_zone))
        .sell(transaction_date=datetime(2021, 1, 3, tzinfo=Settings.system_time_zone))
        # US1234567891
        .buy(
            transaction_date=datetime(2021, 1, 15, tzinfo=Settings.system_time_zone),
            isin_code="US1234567891",
        )
        .df_transaction_list
    )
    with (
        patch(
            "pypmanager.ingest.transaction.transaction_registry.TransactionRegistry."
            "_load_transaction_files",
            return_value=mocked_transactions,
        ),
    ):
        registry = await TransactionRegistry().async_get_current_holding()
        assert len(registry) == 2
        assert registry.index[0] == datetime(
            2021, 1, 3, tzinfo=Settings.system_time_zone
        )
        assert registry.index[1] == datetime(
            2021, 1, 15, tzinfo=Settings.system_time_zone
        )


@pytest.mark.asyncio
async def test_transaction_registry__duplicate_index(
    data_factory: type[DataFactory], caplog: pytest.LogCaptureFixture
) -> None:
    """Test function async_aggregate_ledger_by_year."""
    factory = data_factory()
    mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        )
        .buy(transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone))
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
        assert len(registry) == 2
        assert "Index has duplicate dates" in caplog.text


@pytest.mark.asyncio
async def test_transaction_registry__all_sold__then_buy(
    data_factory: type[DataFactory],
) -> None:
    """Test the registry when everything has been sold and then we buy again."""
    factory = data_factory()
    mocked_transactions = (
        factory.buy(
            transaction_date=datetime(2021, 1, 1, tzinfo=Settings.system_time_zone)
        )
        .buy(
            price=20,
            transaction_date=datetime(2021, 2, 1, tzinfo=Settings.system_time_zone),
        )
        .sell(transaction_date=datetime(2021, 3, 1, tzinfo=Settings.system_time_zone))
        .sell(
            price=1.0,
            transaction_date=datetime(2021, 4, 1, tzinfo=Settings.system_time_zone),
        )
        .buy(
            transaction_date=datetime(2021, 5, 1, tzinfo=Settings.system_time_zone),
        )
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

        assert len(registry) == 5

        # Check volume
        assert_array_equal(
            registry[TransactionRegistryColNameValues.SOURCE_VOLUME.value].to_numpy(),
            [10.0, 10.0, 10.0, 10.0, 10.0],
        )

        # Check price
        assert_array_equal(
            registry[TransactionRegistryColNameValues.SOURCE_PRICE.value].to_numpy(),
            [10.0, 20.0, 15.0, 1.0, 10.0],
        )

        # Check amount
        assert_array_equal(
            registry[ColumnNameValues.AMOUNT.value].to_numpy(),
            [100.0, 200.0, 150.0, 10.0, 100.0],
        )

        # Check quantity held
        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value
            ].to_numpy(),
            [10.0, 20.0, 10.0, np.nan, 10.0],
        )

        assert_array_equal(
            registry[TransactionRegistryColNameValues.PRICE_PER_UNIT.value].to_numpy(),
            [10.0, 15.0, 15.0, np.nan, 10.0],
        )

        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.CALC_ADJUSTED_QUANTITY_HELD_IS_RESET.value
            ].to_numpy(),
            [False, False, False, True, False],
        )

        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.CALC_TURNOVER_OR_OTHER_CF.value
            ].to_numpy(),
            [-100.0, -200.0, 150.0, 10.0, -100.0],
        )

        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.CASH_FLOW_NET_FEE_NOMINAL.value
            ].to_numpy(),
            [-101.0, -201.0, 149.0, 9.0, -101.0],
        )

        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.CASH_FLOW_GROSS_FEE_NOMINAL.value
            ].to_numpy(),
            [-100.0, -200.0, 150.0, 10.0, -100.0],
        )

        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value
            ].to_numpy(),
            [None, None, None, None, None],
        )

        assert_array_equal(
            registry[TransactionRegistryColNameValues.CALC_PNL_TRADE.value].to_numpy(),
            [np.nan, np.nan, -1.0, -141.0, np.nan],
        )

        assert_array_equal(
            registry[TransactionRegistryColNameValues.CALC_PNL_TOTAL.value].to_numpy(),
            [0, 0, -1.0, -141.0, 0],
        )

        assert_array_equal(
            registry[
                TransactionRegistryColNameValues.META_TRANSACTION_YEAR.value
            ].to_numpy(),
            [2021, 2021, 2021, 2021, 2021],
        )


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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
            "source_account_name",
            "amount",
            "calc_agg_sum_quantity_held",
            "calc_avg_price_per_unit",
            "calc_agg_sum_quantity_held_is_reset",
            "calc_turnover_or_cash_flow",
            "calc_cf_net_fee_nominal_ccy",
            "calc_cf_gross_fee_nominal_ccy",
            "calc_pnl_transaction_dividend",
            "calc_pnl_transaction_trade",
            "calc_pnl_transaction_total",
            "meta_transaction_year",
        ]
