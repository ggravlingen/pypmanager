"""Init."""
import logging
import logging.config
import sys

import pandas as pd


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
        "verbose": {
            "()": VerboseFormatter,
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": [
            "console",
        ],
        "level": "INFO",
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

pd.set_option("display.max_columns", None)
