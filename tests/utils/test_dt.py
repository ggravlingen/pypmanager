"""Test date utilities."""
from datetime import date
from unittest.mock import patch

import pytest

from pypmanager.utils.dt import async_get_last_n_quarters, get_previous_quarter


@pytest.mark.asyncio
async def test_async_get_last_n_quarters() -> None:
    """Test function async_get_last_n_quarters."""
    with patch("pypmanager.utils.dt._get_current_date", return_value=date(2023, 8, 5)):
        result = await async_get_last_n_quarters(no_quarters=2)
        assert result == [
            date(2023, 3, 31),
            date(2023, 6, 30),
        ]


@pytest.mark.parametrize(
    "report_date, expected_date",
    [
        (date(2023, 12, 10), date(2023, 9, 30)),
        (date(2023, 9, 15), date(2023, 6, 30)),
        (date(2023, 5, 15), date(2023, 3, 31)),
        (date(2023, 2, 15), date(2022, 12, 31)),
    ],
)
def test_get_previous_quarter(report_date: date, expected_date: date) -> None:
    """Test function get_previous_quarter."""
    assert get_previous_quarter(report_date=report_date) == expected_date
