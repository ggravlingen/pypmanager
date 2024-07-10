"""Tests for template utils."""

from __future__ import annotations

import pytest

from pypmanager.server.templates import (
    load_template,
)


@pytest.mark.asyncio()
async def test_load_template() -> None:
    """Test function load_template."""
    function_result = await load_template(template_name="index.html")
    assert "main.js" in function_result
