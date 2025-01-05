"""Global constants."""

from enum import IntEnum


class HttpStatusCodes(IntEnum):
    """HTTP status codes."""

    OK = 200
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
