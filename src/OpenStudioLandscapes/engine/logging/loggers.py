import logging as log

try:
    # Place this before the third-party packages are imported!
    import logging.config as log_config
    from OpenStudioLandscapes.engine.logging.logging import LOGGING_SCHEMA
    log_config.dictConfig(LOGGING_SCHEMA)
except ImportError as e:
    raise ImportError(e) from e

CLI_LOGGER = log.getLogger("OpenStudioLandscapes.cli")
DISCOVERY_LOGGER = log.getLogger("OpenStudioLandscapes.discovery")
ENGINE_LOGGER = log.getLogger("OpenStudioLandscapes.engine")
FEATURE_LOGGER = log.getLogger("OpenStudioLandscapes.Features")
