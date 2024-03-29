"""Tests for the Avanza loader."""

from unittest.mock import patch

from pypmanager.loader_transaction.avanza import AvanzaLoader
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_data", "tests/fixtures/")
def test_avanza_loader() -> None:
    """Test AvanzaLoader."""
    loader = AvanzaLoader()

    # Test the pre_process_df method
    loader.pre_process_df()

    assert "Resultat" not in loader.df_final.columns

    df_avanza = AvanzaLoader().df_final

    assert len(df_avanza) > 0
