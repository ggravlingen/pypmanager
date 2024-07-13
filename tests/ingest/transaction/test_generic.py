"""Tests for the generic loader."""

from unittest.mock import patch

from pypmanager.ingest.transaction.generic import GenericLoader
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_data", "tests/fixtures/")
def test_misc_loader() -> None:
    """Test GenericLoader."""
    df_misc = GenericLoader().df_final

    assert len(df_misc) > 0
