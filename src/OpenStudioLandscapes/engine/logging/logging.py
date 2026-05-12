import logging
import os
import pathlib
from typing import Dict

LOGS_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get(
        key="OPENSTUDIOLANDSCAPES__LOGS_ROOT",
        default="~/.config/OpenStudioLandscapes",
    )
).expanduser().joinpath(".logs")
LOGS_ROOT.mkdir(parents=True, exist_ok=True)


# This configures the OpenStudioLandscapes loggers.
# The Dagster loggers stay unaffected by these.


# Resources:
# - [A Complete Guide to Linux Log File Locations and Their Usage](https://last9.io/blog/linux-log-file-locations/)
# - [Mastering Python Logging: A Guide to dictConfig() Troubleshooting and Alternatives](https://runebook.dev/en/docs/python/library/logging.config/logging.config.dictConfig)
# - [](https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig)
#
# Follow logs:
# - [](https://unix.stackexchange.com/a/687072/535903)
#
# Dagster Logging:
# - [Dagster Logging](https://docs.dagster.io/guides/log-debug/logging)


ROOT_LOGGER_DEFAULT = logging.DEBUG
CONSOLE_HANDLER_DEFAULT = logging.DEBUG


FORMAT_CONSOLE = "[{asctime}] [{levelname:<8}]:    [{name}] {message}"
FORMAT_FILE = '[{asctime}] [{levelname:<8}] [{threadName}|{thread}], File "{pathname}", line {lineno}, in {funcName}:     [{name}] {message}'

DATE_FMT = "%m-%d-%Y %H:%M:%S"
STYLE = "{"
PROPAGATE = False
DISABLE_EXISTING_LOGGERS = False


LOGGING_SCHEMA: Dict = {
    "version": 1,
    "disable_existing_loggers": DISABLE_EXISTING_LOGGERS,
    "formatters": {
        "console_formatter": {
            "format": FORMAT_CONSOLE,
            "style": STYLE,
            "datefmt": DATE_FMT,
        },
        "file_formatter": {
            "format": FORMAT_FILE,
            "style": STYLE,
            "datefmt": DATE_FMT,
        },
    },
    "handlers": {
        "console": {
            "level": os.environ.get("OPENSTUDIOLANDSCAPES__VERBOSITY"),
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
        },
        "cli_filehandler": {
            "level": os.environ.get("OPENSTUDIOLANDSCAPES__VERBOSITY"),
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filename": os.path.join(LOGS_ROOT, "cli.log"),
            "formatter": "file_formatter",
        },
        "discovery_filehandler": {
            "level": os.environ.get("OPENSTUDIOLANDSCAPES__VERBOSITY"),
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filename": os.path.join(LOGS_ROOT, "discovery.log"),
            "formatter": "file_formatter",
        },
        "engine_filehandler": {
            "level": os.environ.get("OPENSTUDIOLANDSCAPES__VERBOSITY"),
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filename": os.path.join(LOGS_ROOT, "engine.log"),
            "formatter": "file_formatter",
        },
        # "features_filehandler": {
        #     "level": os.environ.get("OPENSTUDIOLANDSCAPES__VERBOSITY"),
        #     "class": "logging.handlers.TimedRotatingFileHandler",
        #     "when": "midnight",
        #     "interval": 1,
        #     "backupCount": 7,
        #     "filename": os.path.join(LOG_ROOT, "features.log"),
        #     "formatter": "file_formatter",
        # },
    },
    "loggers": {
        "OpenStudioLandscapes.cli": {
            "handlers": ["console", "cli_filehandler"],
            "propagate": PROPAGATE,
            # 'level': 'WARNING',
        },
        "OpenStudioLandscapes.discovery": {
            "handlers": ["console", "discovery_filehandler"],
            "propagate": PROPAGATE,
            # 'level': 'WARNING',
        },
        # 'OpenStudioLandscapes.engine.utils': {
        #     'handlers': ['console', 'utils_filehandler'],
        #     'propagate': False,
        #     'level': 'WARNING',
        # },
        # 'OpenStudioLandscapes.engine.common_assets': {
        #     'handlers': ['console', 'utils_filehandler'],
        #     'propagate': False,
        #     'level': 'WARNING',
        # },
        # 'OpenStudioLandscapes.engine.compose_scopes': {
        #     'handlers': ['console', 'compose_scopes_filehandler'],
        #     'propagate': False,
        #     'level': 'WARNING',
        # },
        "OpenStudioLandscapes.engine": {
            "handlers": ["console", "engine_filehandler"],
            "propagate": PROPAGATE,
            # 'level': 'WARNING',
        },
        # "OpenStudioLandscapes.Features": {
        #     "handlers": ["console", "features_filehandler"],
        #     "propagate": False,
        #     # 'level': 'WARNING',
        # },
        # 'urllib3': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'selenium': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'asyncio': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'omxplayer': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
    },
    "root": {
        "level": logging.getLevelName(ROOT_LOGGER_DEFAULT),
        "handlers": ["console"],
    },
}
