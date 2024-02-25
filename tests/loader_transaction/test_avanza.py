"""Tests for the Avanza loader."""

from unittest.mock import patch

from pypmanager.loader_transaction.avanza import AvanzaLoader
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_data", "tests/fixtures/")
def test_avanza_loder() -> None:
    """Test AvanzaLoader."""
    df_avanza = AvanzaLoader().df_final

    assert len(df_avanza) > 0
