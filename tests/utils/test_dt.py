"""Test date utilities."""

from datetime import datetime

from freezegun.api import FrozenDateTimeFactory
import pytest

from pypmanager.settings import Settings
from pypmanager.utils.dt import async_get_last_n_quarters, get_previous_quarter


@pytest.mark.asyncio()
async def test_async_get_last_n_quarters(
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test function async_get_last_n_quarters."""
    freezer.move_to(datetime(2023, 8, 5, tzinfo=Settings.system_time_zone))
    result = await async_get_last_n_quarters(no_quarters=2)
    assert result == [
        datetime(2023, 3, 31, tzinfo=Settings.system_time_zone),
        datetime(2023, 6, 30, tzinfo=Settings.system_time_zone),
    ]


@pytest.mark.parametrize(
    ("report_date", "expected_date"),
    [
        (
            datetime(2023, 12, 10, tzinfo=Settings.system_time_zone),
            datetime(2023, 9, 30, tzinfo=Settings.system_time_zone),
        ),
        (
            datetime(2023, 9, 15, tzinfo=Settings.system_time_zone),
            datetime(2023, 6, 30, tzinfo=Settings.system_time_zone),
        ),
        (
            datetime(2023, 5, 15, tzinfo=Settings.system_time_zone),
            datetime(2023, 3, 31, tzinfo=Settings.system_time_zone),
        ),
        (
            datetime(2023, 2, 15, tzinfo=Settings.system_time_zone),
            datetime(2022, 12, 31, tzinfo=Settings.system_time_zone),
        ),
    ],
)
def test_get_previous_quarter(report_date: datetime, expected_date: datetime) -> None:
    """Test function get_previous_quarter."""
    assert get_previous_quarter(report_date=report_date) == expected_date
