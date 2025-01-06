"""Tests for the Lysa loader."""

from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction import TransactionTypeValues
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.lysa import LysaLoader, _replace_fee_name
from pypmanager.settings import TypedSettings


@pytest.mark.asyncio
@patch.object(TypedSettings, "dir_transaction_data", "tests/fixtures/transactions")
async def test_lysa_loader() -> None:
    """Test LysaLoader."""
    async with LysaLoader() as loader:
        df_lysa = loader.df_final
        assert len(df_lysa) > 0


@pytest.mark.asyncio
@patch.object(TypedSettings, "dir_transaction_data", "tests/fixtures/transactions")
async def test_lysa_loader__async_validate_isin(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test LysaLoader.async_validate_isin."""
    async with LysaLoader() as loader:
        # Replace all ISIN values with None for test purposes
        loader.df_final[TransactionRegistryColNameValues.SOURCE_ISIN.value] = None
        await loader.async_validate_isin()
        assert "ISIN code not found for security name" in caplog.text


@pytest.mark.parametrize(
    ("transaction_type", "name", "expected_result"),
    [
        (TransactionTypeValues.FEE.value, "Some Name", "Lysa management fee"),
        (TransactionTypeValues.CASHBACK.value, "Another Name", "Another Name"),
    ],
)
def test_replace_fee_name(
    transaction_type: str,
    name: str,
    expected_result: str,
) -> None:
    """Test function _replace_fee_name."""
    data = {
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE: [transaction_type],
        TransactionRegistryColNameValues.SOURCE_NAME_SECURITY: [name],
    }
    df_test_data = pd.DataFrame(data)

    # Call the function
    function_result = _replace_fee_name(df_test_data.iloc[0])

    # Assert the result
    assert function_result == expected_result
