"""Tests for template utils."""

from __future__ import annotations

import math
from typing import Any

import pytest

from pypmanager.server.templates import (
    format_decimals,
    format_none,
    load_template,
    static_file2base64,
)


@pytest.mark.asyncio()
async def test_load_template() -> None:
    """Test function load_template."""
    function_result = await load_template(template_name="index.html")
    assert "main.js" in function_result


@pytest.mark.parametrize(
    ("value", "no_decimals", "expected_output"),
    [
        (1234.5678, 2, "1,234.57"),
        (1234.5678, 0, "1,235"),
        (1234.5678, 4, "1,234.5678"),
        (None, 2, "–"),  # noqa: RUF001
        (math.nan, 2, "–"),  # noqa: RUF001
        ("abc", 2, "–"),  # noqa: RUF001
    ],
)
def test_format_decimals(value: Any, no_decimals: int, expected_output: str) -> None:  # noqa: ANN401
    """Test function format_decimals."""
    assert format_decimals(value, no_decimals) == expected_output


@pytest.mark.parametrize(
    ("value", "expected_output"),
    [
        (1234.5678, 1234.5678),
        (None, "–"),  # noqa: RUF001
        (math.nan, "–"),  # noqa: RUF001
    ],
)
def test_format_none(
    value: float | None | math.nan,
    expected_output: float | str,
) -> None:
    """Test function format_none."""
    assert format_none(value) == expected_output


def test_static_file2base64() -> None:
    """Test function static_file2base64."""
    function_result = static_file2base64("favicon.ico")
    assert "iVBORw0KG" in function_result
