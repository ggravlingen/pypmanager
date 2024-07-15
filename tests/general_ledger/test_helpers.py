"""Test helpers."""

import pytest

from pypmanager.general_ledger import async_aggregate_ledger_by_year


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_mock_transactions_general_ledger")
async def test_async_aggregate_ledger_by_year() -> None:
    """Test function async_aggregate_ledger_by_year."""
    ledger = await async_aggregate_ledger_by_year()
    assert ledger.columns.to_list() == ["year", "ledger_account", "net"]
    assert len(ledger) == 1
