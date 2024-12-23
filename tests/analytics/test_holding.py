"""Test helpers."""

from __future__ import annotations

from pypmanager.analytics.holding import get_market_data


def test_get_market_data() -> None:
    """Test async_get_market_data."""
    result = get_market_data()

    assert result is not None
    assert len(result) == 1
    assert result.iloc[0].isin_code == "LU0051755006"


def test_get_market_data__filter() -> None:
    """Test async_get_market_data with filter."""
    result = get_market_data(isin_code="LU0051755006")

    assert result is not None
    assert len(result) == 1
    assert result.iloc[0].isin_code == "LU0051755006"