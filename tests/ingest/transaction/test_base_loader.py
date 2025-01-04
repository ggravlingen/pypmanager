"""Tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from pypmanager.ingest.transaction.base_loader import TransactionLoader, _get_filename


@pytest.mark.parametrize(
    ("file_path", "expected"),
    [
        (Path("/path/to/file-abc.csv"), "Abc"),
        (Path("/path/to/file.csv"), "File"),
        (Path("/path/to/another-file-456.csv"), "Another"),
    ],
)
def test_get_filename(file_path: Path, expected: str) -> None:
    """Test the _get_filename function."""
    assert _get_filename(file_path) == expected


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
