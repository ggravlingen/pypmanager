"""Tests for the Avanza loader."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction.avanza import AvanzaLoader, _transaction_type
from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.settings import TypedSettings


@pytest.mark.asyncio
@patch.object(TypedSettings, "dir_transaction_data", "tests/fixtures/transactions")
async def test_avanza_loader() -> None:
    """Test AvanzaLoader."""
    loader = AvanzaLoader()
    await loader.async_load()

    df_avanza = loader.df_final
    assert "Resultat" not in df_avanza.columns

    assert len(df_avanza) > 0


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        (
            pd.Series(
                {
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: "Övrigt",
                    TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: (
                        "Avkastningsskatt"
                    ),
                }
            ),
            TransactionTypeValues.FEE,
        ),
        (
            pd.Series(
                {
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: "Övrigt",
                    TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Flyttavg",
                }
            ),
            TransactionTypeValues.FEE_CREDIT,
        ),
        (
            pd.Series(
                {
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: "Köp",
                    TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: (
                        "Some Security"
                    ),
                }
            ),
            "Köp",
        ),
    ],
)
def test_transaction_type(row: pd.Series, expected: str) -> None:
    """Test the _transaction_type function."""
    assert _transaction_type(row) == expected
