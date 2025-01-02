"""Tests for settings."""

from pathlib import Path

from pypmanager.settings import TypedSettings


def test_file_market_data_config() -> None:
    """Test property file_market_data_config."""
    settings = TypedSettings()
    folder_path = Path(settings.dir_config)
    expected_path = folder_path / "market_data.yaml"
    assert settings.file_market_data_config == expected_path
