"""Tests for the Lysa loader."""

from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction import ColumnNameValues, TransactionTypeValues
from pypmanager.ingest.transaction.lysa import LysaLoader, _replace_fee_name
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_data", "tests/fixtures/")
def test_lysa_loader() -> None:
    """Test LysaLoader."""
    df_lysa = LysaLoader().df_final

    assert len(df_lysa) > 0


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
        ColumnNameValues.TRANSACTION_TYPE: [transaction_type],
        ColumnNameValues.NAME: [name],
    }
    df_test_data = pd.DataFrame(data)

    # Call the function
    function_result = _replace_fee_name(df_test_data.iloc[0])

    # Assert the result
    assert function_result == expected_result
