"""Tests for the generic loader."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pypmanager.ingest.transaction.pareto_securities import ParetoSecuritiesLoader
from pypmanager.settings import TypedSettings


@pytest.mark.asyncio
@patch.object(
    TypedSettings,
    "dir_transaction_data_local",
    "tests/fixtures/transactions",
)
async def test_pareto_loader() -> None:
    """Test ParetoSecuritiesLoader."""
    async with ParetoSecuritiesLoader() as loader:
        df_generic = loader.df_final
        assert len(df_generic) > 0
