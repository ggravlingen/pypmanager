"""Date utilities."""
from datetime import date, timedelta

QUARTER_ENDS = [(3, 31), (6, 30), (9, 30), (12, 31)]


def _get_current_date() -> date:
    """Return today's date."""
    return date.today()


def get_previous_quarter(report_date: date) -> date:
    """Return the previous quarter."""
    if report_date.month < 4:
        return date(report_date.year - 1, 12, 31)

    if report_date.month < 7:
        return date(report_date.year, 3, 31)

    if report_date.month < 10:
        return date(report_date.year, 6, 30)

    return date(report_date.year, 9, 30)


async def async_get_last_n_quarters(no_quarters: int) -> list[date]:
    """Return a list of fiscal quarter ends."""
    current_date = _get_current_date()
    last_quarter = get_previous_quarter(report_date=current_date)
    quarter_ends: list[date] = []

    quarter_ends.append(last_quarter)

    for _ in range(no_quarters - 1):
        t_minus_1 = last_quarter - timedelta(1)
        last_quarter = get_previous_quarter(report_date=t_minus_1)
        quarter_ends.append(last_quarter)

    return quarter_ends[::-1]
