import copy
import importlib
import os

from dagster import Definitions, get_dagster_logger

from OpenStudioLandscapes.engine.discovery.discovery import FUNCTIONAL_FEATURES
from OpenStudioLandscapes.engine.utils import *

LOGGER = get_dagster_logger(__name__)

# Base Definitions
imports_engine = [
    "OpenStudioLandscapes.engine.base.definitions",
    "OpenStudioLandscapes.engine.env.definitions",
    # "OpenStudioLandscapes.engine.landscape_map.definitions",
    # "OpenStudioLandscapes.engine.distributable.definitions",
]

e_ = expand_dict_vars(
    dict_to_expand=copy.deepcopy(os.environ),
    kv=os.environ,
)


# ComposeScope Definitions
imports_engine.extend(
    [
        "OpenStudioLandscapes.engine.compose_scopes.default.definitions",
        # "OpenStudioLandscapes.engine.compose_scopes.license_server.definitions",
        # "OpenStudioLandscapes.engine.compose_scopes.worker.definitions",
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


modules.extend([i["definitions"] for i in FUNCTIONAL_FEATURES])

# for useable_feature in USABLE_FEATURES:
#     LOGGER.error(f"{useable_feature = }")


defs = Definitions.merge(
    *[i.defs for i in modules],
)
