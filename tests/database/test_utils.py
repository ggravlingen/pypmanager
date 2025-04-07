"""Tests for database utils."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import Connection

from pypmanager.database.utils import check_table_exists


@pytest.mark.parametrize(
    ("existing_tables", "table_name", "expected_result"),
    [
        (["market_data", "transactions"], "market_data", True),
        (["market_data", "transactions"], "non_existent_table", False),
        ([], "any_table", False),
    ],
)
def test_check_table_exists(
    existing_tables: list[str],
    table_name: str,
    expected_result: bool,
) -> None:
    """Test check_table_exists with various table scenarios."""
    mock_connection = MagicMock(spec=Connection)
    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = existing_tables

    with patch("pypmanager.database.utils.inspect", return_value=mock_inspector):
        result = check_table_exists(mock_connection, table_name)

    assert result == expected_result
