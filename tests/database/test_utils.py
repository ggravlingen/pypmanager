"""Tests for database utils."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy.orm import Mapped, mapped_column

from pypmanager.database.utils import Base, async_upsert_data, check_table_exists


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


class MockModel(Base):
    """Mock SQLAlchemy model for testing."""

    __tablename__ = "mock_table"
    isin: Mapped[str] = mapped_column(primary_key=True)


@pytest.mark.asyncio
async def test_async_upsert_data_success() -> None:
    """Test async_upsert_data successfully upserts data."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_data_list = [MockModel(), MockModel()]

    # Act
    await async_upsert_data(session=mock_session, data_list=mock_data_list)

    # Assert
    assert mock_session.merge.call_count == len(mock_data_list)
    mock_session.merge.assert_any_call(mock_data_list[0])
    mock_session.merge.assert_any_call(mock_data_list[1])
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_async_upsert_data_failure(caplog: pytest.LogCaptureFixture) -> None:
    """Test async_upsert_data rolls back on failure."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_data_list = [MockModel()]
    mock_session.merge.side_effect = Exception("Mock exception")

    await async_upsert_data(session=mock_session, data_list=mock_data_list)

    assert "No successful merges to commit, all 1 items failed" in caplog.text

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
