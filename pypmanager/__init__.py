"""Init."""
import logging
import logging.config
import sys

from colorlog import ColoredFormatter
import pandas as pd

# Disable logger
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)


class VerboseFormatter(logging.Formatter):
    """Custom log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log string."""
        return (
            f"[{self.formatTime(record)}] [{record.levelname}] "
            f"{record.name}: {record.getMessage()}"
        )


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": ColoredFormatter,
            "format": (
                "%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            ),
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": [
            "console",
        ],
        "level": "DEBUG",
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

pd.set_option("display.max_columns", None)
