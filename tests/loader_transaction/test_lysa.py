"""Tests for the Lysa loader."""

from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues
from pypmanager.loader_transaction.lysa import LysaLoader, _replace_fee_name
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_data", "tests/fixtures/")
def test_lysa_loader() -> None:
    """Test LysaLoader."""
    df_lysa = LysaLoader().df_final

    assert len(df_lysa) > 0


@pytest.mark.parametrize(
    "transaction_type, name, expected_result",
    [
        (TransactionTypeValues.FEE.value, "Some Name", "Lysa management fee"),
        ("Other Type", "Another Name", "Another Name"),
        # Add more test cases as needed
    ],
)
def test_replace_fee_name(transaction_type, name, expected_result):
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
