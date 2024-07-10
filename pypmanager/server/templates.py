"""Template management."""

from typing import Any

from jinja2 import Environment, FileSystemLoader

from pypmanager.settings import Settings


async def load_template(
    template_name: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Load html template."""
    env = Environment(
        loader=FileSystemLoader(Settings.dir_templates),
        autoescape=True,
    )
    template = env.get_template(template_name)

    if context:
        return template.render(context)

    return template.render()
