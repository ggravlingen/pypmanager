"""Tests."""

from __future__ import annotations

from pypmanager.ingest.transaction.base_loader import (
    TransactionLoader,
)


def test_empty_loader() -> None:
    """Test the base loader class with empty data."""

    class MockLoader(TransactionLoader):
        """Mock the TransactionLoader."""

        file_pattern = "abc123"
        date_format_pattern = "%Y-%m-%d"

        def pre_process_df(self: MockLoader) -> None:
            """Mock method."""

    mock_loader = MockLoader()

    assert len(mock_loader.df_final) == 0
