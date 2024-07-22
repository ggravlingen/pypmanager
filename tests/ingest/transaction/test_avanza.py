"""Tests for the Avanza loader."""

from unittest.mock import patch

from pypmanager.ingest.transaction.avanza import AvanzaLoader
from pypmanager.settings import TypedSettings


@patch.object(TypedSettings, "dir_transaction_data", "tests/fixtures/transactions")
def test_avanza_loader() -> None:
    """Test AvanzaLoader."""
    loader = AvanzaLoader()

    # Test the pre_process_df method
    loader.pre_process_df()

    assert "Resultat" not in loader.df_final.columns

    df_avanza = AvanzaLoader().df_final

    assert len(df_avanza) > 0
