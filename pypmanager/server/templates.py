"""Template management."""

import base64
from datetime import datetime
import locale
from pathlib import Path
from typing import Any

import humanize
from jinja2 import Environment, FileSystemLoader
import markupsafe
import pandas as pd

from pypmanager.settings import Settings

# The use of en dash is intentional
ATTR_NONE = "–"  # noqa: RUF001


def _load_environment_and_filter() -> Environment:
    """Load Jinja environment and add filters."""
    env = Environment(
        loader=FileSystemLoader("pypmanager/server/templates"),
        autoescape=True,
    )
    env.filters["static_file2base64"] = static_file2base64
    env.filters["format_decimals"] = format_decimals
    env.filters["format_none"] = format_none
    env.filters["format_pct"] = format_pct
    env.filters["format_date"] = format_date

    return env


async def load_template(
    template_name: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Load html template."""
    env = _load_environment_and_filter()
    template = env.get_template(template_name)

    if context:
        return template.render(context)

    return template.render()


def static_file2base64(file: str) -> markupsafe.Markup:
    """Convert a file in the static folder to base 64."""
    file_full_path = Path(Settings.dir_static) / file

    path = Path(file_full_path)

    with path.open("rb") as _file:
        encoded_bytes = base64.b64encode(_file.read())
        return markupsafe.Markup(encoded_bytes.decode("utf-8"))


def format_decimals(value: float | None, no_decimals: int = 2) -> str | None:
    """Format a value using n decimals."""
    if value is None or value == 0 or pd.isna(value):
        return ATTR_NONE

    locale.setlocale(locale.LC_NUMERIC, "en_US.UTF-8")

    try:
        return locale.format_string(f"%.{no_decimals}f", value, grouping=True)
    except (ValueError, TypeError):
        return ATTR_NONE


def format_none(value: str | float | None) -> str | float:
    """Return value, or en dash if None."""
    if value is None or pd.isna(value):
        return ATTR_NONE

    return value


def format_pct(value: str | float | None, decimals: int = 1) -> str | float:
    """Return per cent, or en dash if None."""
    if value is None or pd.isna(value):
        return ATTR_NONE

    template = "{" + f":.{decimals}%" + "}"
    return template.format(value)


def format_date(value: str) -> str:
    """Return date, or en dash if None."""
    if value is None or pd.isna(value):
        return ATTR_NONE

    value_as_date = datetime.strptime(value, "%Y-%m-%d").date()  # noqa: DTZ007

    return humanize.naturalday(value_as_date)
