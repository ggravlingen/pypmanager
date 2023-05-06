"""Template management."""

import base64
import locale
import os
from typing import Any

from jinja2 import Environment, FileSystemLoader
import markupsafe

from pypmanager.settings import Settings


def _load_environment_and_filter() -> Environment:
    """Load Jinja environment and add filters."""
    env = Environment(
        loader=FileSystemLoader("pypmanager/server/templates"), autoescape=True
    )
    env.filters["static_file2base64"] = static_file2base64
    env.filters["format_decimals"] = format_decimals

    return env


async def load_template(
    template_name: str, context: dict[str, Any] | None = None
) -> str:
    """Load html template."""
    env = _load_environment_and_filter()
    template = env.get_template(template_name)

    if context:
        return template.render(context)

    return template.render()


def static_file2base64(file: str) -> markupsafe.Markup:
    """Convert a file in the static folder to base 64."""
    file = os.path.join(Settings.DIR_STATIC, file)

    with open(file, "rb") as _file:
        encoded_bytes = base64.b64encode(_file.read())
        return markupsafe.Markup(encoded_bytes.decode("utf-8"))


def format_decimals(value: float | None, no_decimals: int = 2):
    """Format a value using n decimals."""
    if value is None:
        return None

    locale.setlocale(locale.LC_NUMERIC, "en_US.UTF-8")

    try:
        return locale.format_string(f"%.{no_decimals}f", value, grouping=True)
    except ValueError as err:
        print(err)
        return None
