"""Global constants."""

from enum import IntEnum


class HttpStatusCodes(IntEnum):
    """HTTP status codes."""

    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500
