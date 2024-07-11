"""Constants for loaders."""

from enum import IntEnum
import logging

LOGGER = logging.getLogger(__package__)

LOAD_HISTORY_DAYS = 180


class HttpResponseCodeLabels(IntEnum):
    """Represent HTTP response codes."""

    OK = 200
