"""Tests for settings."""

import os

from pypmanager.settings import TypedSettings


def test_dir_data_demo() -> None:
    """Test property dir_data in demo mode."""
    settings = TypedSettings()
    settings.is_demo = True
    assert settings.dir_data == os.path.abspath("data-demo")


def test_dir_data_not_demo() -> None:
    """Test property dir_data in production mode."""
    settings = TypedSettings()
    settings.is_demo = False
    assert settings.dir_data == os.path.abspath("data")


def test_file_market_data_config() -> None:
    """Test property file_market_data_config."""
    settings = TypedSettings()
    expected_path = os.path.abspath(
        os.path.join(settings.dir_config, "market_data.yaml")
    )
    assert settings.file_market_data_config == expected_path
