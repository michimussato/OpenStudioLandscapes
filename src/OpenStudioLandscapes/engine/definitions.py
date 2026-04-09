from dagster import Definitions, get_dagster_logger

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

LOGGER = get_dagster_logger(__name__)


modules = []


package: str
feature: discovery.OpenStudioLandscapesDiscoveredFeature
for package, feature in discovery.DISCOVERED_MODELS.items():
    config: FeatureBaseModel = feature.config
    enabled: bool = config.enabled
    if enabled:
        modules.append(feature.definitions_object)
    else:
        continue


# This loads the definitions from all the available (and
# enabled) Features.
# Todo:
#  - [ ] migrate to Code Locations
defs = Definitions.merge(
    *[i.defs for i in modules],
)
