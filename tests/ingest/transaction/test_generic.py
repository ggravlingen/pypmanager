"""Tests for the generic loader."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.generic import GenericLoader, _replace_fee_name
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_transaction_data", "tests/fixtures/transactions")
def test_misc_loader() -> None:
    """Test GenericLoader."""
    df_misc = GenericLoader().df_final

    assert len(df_misc) > 0


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        (
            pd.Series(
                {
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: (
                        "Plattformsavgift"
                    ),
                    TransactionRegistryColNameValues.SOURCE_BROKER.value: "SAVR",
                    TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Old Name",
                }
            ),
            "SAVR management fee",
        ),
        (
            pd.Series(
                {
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: "Other",
                    TransactionRegistryColNameValues.SOURCE_BROKER.value: "SAVR",
                    TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: "Old Name",
                }
            ),
            "Old Name",
        ),
    ],
)
def test_replace_fee_name(row: pd.Series, expected: str) -> None:
    """Test the _replace_fee_name function."""
    assert _replace_fee_name(row) == expected
