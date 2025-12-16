import copy
import importlib
import os

from dagster import Definitions, get_dagster_logger

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel
from OpenStudioLandscapes.engine.utils import *

LOGGER = get_dagster_logger(__name__)

# Base Definitions
imports_engine = [
    "OpenStudioLandscapes.engine.base.definitions",
    "OpenStudioLandscapes.engine.env.definitions",
]

e_ = expand_dict_vars(
    dict_to_expand=copy.deepcopy(os.environ),
    kv=os.environ,
)


# Additional Definitions
#
# This structure is for debugging
#
# These modules have a layered dependency:
# the latter depends on the prior.
# To disable one of them, disable it and
# every module beneath it.
imports_engine.extend(
    [
        "OpenStudioLandscapes.engine.compose_scopes.default.definitions",
        "OpenStudioLandscapes.engine.landscape_map.definitions",
        "OpenStudioLandscapes.engine.distributable.definitions",
    ]
)


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
