from dagster import get_dagster_logger

from OpenStudioLandscapes.cli import LOGGING_LEVEL_DEFAULT
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel
from OpenStudioLandscapes.engine.discovery import discovery

LOGGER = get_dagster_logger(__name__)
LOGGER.setLevel(LOGGING_LEVEL_DEFAULT)

grafana_installed: bool = (
    "OpenStudioLandscapes.Grafana" in discovery.DISCOVERED_MODELS.keys()
)
LOGGER.info(f"{grafana_installed = }")

if grafana_installed:
    grafana_config: FeatureBaseModel = discovery.DISCOVERED_MODELS[
        "OpenStudioLandscapes.Grafana"
    ].config
    LOGGER.info(f"{grafana_config = }")

    grafana_enabled: bool = grafana_config.enabled
    LOGGER.info(f"{grafana_enabled = }")
else:
    grafana_enabled: bool = False
    LOGGER.info(f"{grafana_enabled = }")

GRAFANA_AVAILABLE: bool = all(
    [
        grafana_installed,
        grafana_enabled,
    ],
)
