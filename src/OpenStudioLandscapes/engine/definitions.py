import importlib

from dagster import Definitions, get_dagster_logger

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

LOGGER = get_dagster_logger(__name__)

# Base Definitions
imports_engine = [
    "OpenStudioLandscapes.engine.env.definitions",
]


modules = []


for core in imports_engine:
    try:
        module_object = importlib.import_module(core)
        modules.append(module_object)
    except ModuleNotFoundError as e:
        LOGGER.error(f"Engine setup failed to complete: {e}")
        raise e

package: str
feature: discovery.OpenStudioLandscapesDiscoveredFeature
for package, feature in discovery.DISCOVERED_MODELS.items():
    config: FeatureBaseModel = feature.config
    enabled: bool = config.enabled
    if enabled:
        modules.append(feature.definitions_object)
    else:
        continue


defs = Definitions.merge(
    *[i.defs for i in modules],
)
