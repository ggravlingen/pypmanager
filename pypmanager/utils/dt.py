"""Date utilities."""

from datetime import datetime, timedelta
from enum import IntEnum

from pypmanager.settings import Settings

QUARTER_ENDS = [(3, 31), (6, 30), (9, 30), (12, 31)]


class MonthEnumValues(IntEnum):
    """Represent months."""

    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12


class WeekDayEnumValues(IntEnum):
    """Represent week days."""

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


def get_previous_quarter(report_date: datetime) -> datetime:
    """Return the previous quarter."""
    if report_date.month < MonthEnumValues.APR:
        return datetime(report_date.year - 1, 12, 31, tzinfo=Settings.system_time_zone)

    if report_date.month < MonthEnumValues.JUL:
        return datetime(report_date.year, 3, 31, tzinfo=Settings.system_time_zone)

    if report_date.month < MonthEnumValues.OCT:
        return datetime(report_date.year, 6, 30, tzinfo=Settings.system_time_zone)

    return datetime(report_date.year, 9, 30, tzinfo=Settings.system_time_zone)


async def async_get_last_n_quarters(no_quarters: int) -> list[datetime]:
    """Return a list of fiscal quarter ends."""
    current_date = datetime.now(tz=Settings.system_time_zone)
    last_quarter = get_previous_quarter(report_date=current_date)
    quarter_ends: list[datetime] = []

    quarter_ends.append(last_quarter)

    for _ in range(no_quarters - 1):
        t_minus_1 = last_quarter - timedelta(1)
        last_quarter = get_previous_quarter(report_date=t_minus_1)
        quarter_ends.append(last_quarter)

    return quarter_ends[::-1]
