"""Tests for template utils."""
from pypmanager.server.templates import format_decimals
import pytest


@pytest.mark.parametrize(
    "value, no_decimals, expected_output",
    [
        (1234.5678, 2, "1,234.57"),
        (1234.5678, 0, "1,235"),
        (1234.5678, 4, "1,234.5678"),
        (None, 2, None),
    ],
)
def test_format_decimals(value, no_decimals, expected_output) -> None:
    """Test function format_decimals."""
    assert format_decimals(value, no_decimals) == expected_output
