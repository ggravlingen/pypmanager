"""Tests."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from pypmanager.ingest.transaction.base_loader import (
    EMPTY_DF,
    TransactionLoader,
    _get_filename,
)
from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues


class MockLoader(TransactionLoader):
    """Mock the TransactionLoader."""

    file_pattern = "abc123"
    date_format_pattern = "%Y-%m-%d"

    def pre_process_df(self: MockLoader) -> None:
        """Mock method."""


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
    mock_loader = MockLoader()
    assert len(mock_loader.df_final) == 0


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        (
            ["file1.csv", "file2.csv"],
            pd.DataFrame(
                {
                    "A": [1, 2, 3, 4],
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: [
                        "2021-01-01",
                        "2021-01-02",
                        "2021-01-03",
                        "2021-01-04",
                    ],
                    TransactionRegistryColNameValues.SOURCE_FILE.value: [
                        "testfile",
                        "testfile",
                        "testfile",
                        "testfile",
                    ],
                }
            ),
        ),
        (
            ["file3.csv"],
            pd.DataFrame(
                {
                    "B": [5, 6],
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: [
                        "2021-01-05",
                        "2021-01-06",
                    ],
                    TransactionRegistryColNameValues.SOURCE_FILE.value: [
                        "testfile",
                        "testfile",
                    ],
                }
            ),
        ),
        ([], EMPTY_DF),
    ],
)
def test_load_data_files(files: list[str], expected: pd.DataFrame) -> None:
    """Test the load_data_files method."""

    def mock_read_csv(file: Path, sep: str) -> pd.DataFrame:  # noqa: ARG001
        if "file1.csv" in str(file):
            return pd.DataFrame(
                {
                    "A": [1, 2],
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: [
                        "2021-01-01",
                        "2021-01-02",
                    ],
                }
            )
        if "file2.csv" in str(file):
            return pd.DataFrame(
                {
                    "A": [3, 4],
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: [
                        "2021-01-03",
                        "2021-01-04",
                    ],
                }
            )
        if "file3.csv" in str(file):
            return pd.DataFrame(
                {
                    "B": [5, 6],
                    TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value: [
                        "2021-01-05",
                        "2021-01-06",
                    ],
                }
            )

        msg = f"Unexpected file: {file}"
        raise ValueError(msg)

    with (
        patch("pandas.read_csv", side_effect=mock_read_csv),
        patch("pathlib.Path.glob", return_value=[Path(f) for f in files]),
        patch(
            "pypmanager.ingest.transaction.base_loader._get_filename",
            return_value="testfile",
        ),
    ):
        loader = MockLoader()
        loader.load_data_files()

    pd.testing.assert_frame_equal(loader.df_final, expected)


def test_validate(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the validate method."""
    with caplog.at_level(logging.ERROR):
        loader = MockLoader()
        loader.df_final = pd.DataFrame({"A": [1, 2]})
        loader.validate()
        assert "ISIN code is missing" in caplog.text
