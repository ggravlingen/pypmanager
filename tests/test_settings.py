"""Tests for settings."""

from pathlib import Path

from pypmanager.settings import TypedSettings


def test_dir_data_demo() -> None:
    """Test property dir_data in demo mode."""
    settings = TypedSettings()
    settings.is_demo = True
    assert "data-demo" in settings.dir_data.name


def test_dir_data_not_demo() -> None:
    """Test property dir_data in production mode."""
    settings = TypedSettings()
    settings.is_demo = False
    assert "data" in settings.dir_data.name


def test_file_market_data_config() -> None:
    """Test property file_market_data_config."""
    settings = TypedSettings()
    folder_path = Path(settings.dir_config)
    expected_path = folder_path / "market_data.yaml"
    assert settings.file_market_data_config == expected_path
