import os
import logging as log
from logging.handlers import TimedRotatingFileHandler
from importlib.metadata import (  # pragma: no cover
    Distribution,
)
from OpenStudioLandscapes.engine.logging.logging import PROPAGATE, FORMAT_CONSOLE, FORMAT_FILE, DATE_FMT, STYLE, LOG_ROOT

try:
    # Place this before the third-party packages are imported!
    import logging.config as log_config

    from OpenStudioLandscapes.engine.logging.logging import LOGGING_SCHEMA

    log_config.dictConfig(LOGGING_SCHEMA)
except ImportError as e:
    # Todo:
    #  - [ ] make fail safe
    #        - [](https://runebook.dev/en/docs/python/library/logging.config/logging.config.dictConfig)
    raise ImportError(f"Could not import OpenStudioLandscapes Loggers: " f"{e}") from e

CLI_LOGGER = log.getLogger("OpenStudioLandscapes.cli")
DISCOVERY_LOGGER = log.getLogger("OpenStudioLandscapes.discovery")
ENGINE_LOGGER = log.getLogger("OpenStudioLandscapes.engine")
# FEATURE_LOGGER = log.getLogger("OpenStudioLandscapes")


def get_feature_logger(
        dist: Distribution,
) -> log.Logger:
    ENGINE_LOGGER.info(f"Configuring logger for {dist.name}...")

    feature_logger: log.Logger = log.getLogger(dist.name)
    feature_logger.setLevel(os.environ.get("OPENSTUDIOLANDSCAPES__VERBOSITY"))
    feature_logger.propagate = PROPAGATE

    console_formatter: log.Formatter = log.Formatter(fmt=FORMAT_CONSOLE, datefmt=DATE_FMT, style=STYLE)
    file_formatter: log.Formatter = log.Formatter(fmt=FORMAT_FILE, datefmt=DATE_FMT, style=STYLE)

    file_handler: TimedRotatingFileHandler = TimedRotatingFileHandler(
        filename=LOG_ROOT.joinpath(f"{dist.name}.log"),
        encoding='utf-8',
        when='midnight',
        interval=1,
        backupCount=7,
    )
    file_handler.setFormatter(file_formatter)

    console_handler: log.StreamHandler = log.StreamHandler()
    console_handler.setFormatter(console_formatter)

    feature_logger.addHandler(console_handler)
    feature_logger.addHandler(file_handler)

    ENGINE_LOGGER.info(f"Logger for {dist.name} configured.")

    feature_logger.info(f"Hello from {dist.name} Logger!")

    return feature_logger
