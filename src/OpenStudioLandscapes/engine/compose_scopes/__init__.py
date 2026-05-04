from OpenStudioLandscapes.engine.logging.loggers import ENGINE_LOGGER as LOGGER

from OpenStudioLandscapes.engine.config.models import FeatureBaseModel
from OpenStudioLandscapes.engine.discovery import discovery


grafana_installed: bool = (
    "OpenStudioLandscapes.Grafana" in discovery.DISCOVERED_MODELS.keys()
)
LOGGER.info(f"{grafana_installed = }")

if grafana_installed:
    grafana_config: FeatureBaseModel = discovery.DISCOVERED_MODELS[
        "OpenStudioLandscapes.Grafana"
    ].config

    grafana_enabled: bool = grafana_config.enabled
    # LOGGER.info(f"{grafana_enabled = }")
    LOGGER.debug(f"{grafana_config = }")
else:
    grafana_enabled: bool = False

LOGGER.info(f"{grafana_enabled = }")

GRAFANA_AVAILABLE: bool = all(
    [
        grafana_installed,
        grafana_enabled,
    ],
)
