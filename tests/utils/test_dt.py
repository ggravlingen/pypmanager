"""Test date utilities."""

from datetime import date, datetime

from freezegun.api import FrozenDateTimeFactory
import pandas as pd
import pytest

from pypmanager.settings import Settings
from pypmanager.utils.dt import (
    async_filter_df_by_date_range,
    async_get_empty_df_with_datetime_index,
    async_get_last_n_quarters,
    get_previous_quarter,
)


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_async_get_empty_df_with_datetime_index() -> None:
    """Test function async_get_empty_df_with_datetime_index."""
    result = await async_get_empty_df_with_datetime_index(
        start_date=date(2024, 12, 15),
        end_date=date(2024, 12, 31),
        market="XNYS",
    )
    assert len(result) == 11
    assert result.index[0] == datetime(2024, 12, 16, tzinfo=Settings.system_time_zone)
    assert result.index[-1] == datetime(2024, 12, 31, tzinfo=Settings.system_time_zone)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("start_date", "end_date", "expected_index", "expected_values"),
    [
        (
            date(2023, 1, 2),
            date(2023, 1, 4),
            pd.date_range(start="2023-01-02", end="2023-01-04", freq="D").tz_localize(
                Settings.system_time_zone
            ),
            [2, 3, 4],
        ),
        (
            date(2022, 12, 31),
            date(2023, 1, 3),
            pd.date_range(start="2023-01-01", end="2023-01-03", freq="D").tz_localize(
                Settings.system_time_zone
            ),
            [1, 2, 3],
        ),
        (
            date(2023, 1, 3),
            date(2023, 1, 6),
            pd.date_range(start="2023-01-03", end="2023-01-05", freq="D").tz_localize(
                Settings.system_time_zone
            ),
            [3, 4, 5],
        ),
        (
            date(2022, 12, 31),
            date(2023, 1, 6),
            pd.date_range(start="2023-01-01", end="2023-01-05", freq="D").tz_localize(
                Settings.system_time_zone
            ),
            [1, 2, 3, 4, 5],
        ),
        (
            date(2023, 1, 3),
            date(2023, 1, 3),
            pd.date_range(start="2023-01-03", end="2023-01-03", freq="D").tz_localize(
                Settings.system_time_zone
            ),
            [3],
        ),
    ],
)
async def test_async_filter_df_by_date_range(
    start_date: date,
    end_date: date,
    expected_index: pd.DatetimeIndex,
    expected_values: list[int],
) -> None:
    """Test function async_filter_df_by_date_range."""
    # Sample DataFrame
    data = {"value": [1, 2, 3, 4, 5]}
    index = pd.date_range(start="2023-01-01", periods=5, freq="D").tz_localize(
        Settings.system_time_zone
    )
    df_test_data = pd.DataFrame(data, index=index)

    result = await async_filter_df_by_date_range(df_test_data, start_date, end_date)
    assert result.index.equals(expected_index)
    assert result["value"].tolist() == expected_values
