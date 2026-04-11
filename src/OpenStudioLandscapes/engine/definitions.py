import importlib

from dagster import Definitions, get_dagster_logger

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

LOGGER = get_dagster_logger(__name__)

# Base Definitions
code_locations = [
    "OpenStudioLandscapes.engine.env.definitions",

    # default definitions file is for Single Code Location where AssetSpec clash with AssetDefinitions
    # "OpenStudioLandscapes.engine.base.definitions",
    # _with_upstream_specs definitions file is for Multi Code Location or isolated testing/development
    # (contains AssetDefinitions and upstream AssetSpecs)
    {
        "default": "OpenStudioLandscapes.engine.base.definitions",
        "_with_upstream_specs": "OpenStudioLandscapes.engine.base._definitions_with_upstream_specs",
    }["default"],

    # "OpenStudioLandscapes.engine.vfx_reference.definitions",
]


# Additional Definitions
#
# This structure is for debugging
#
# These modules have a layered dependency:
# the latter depends on the prior.
# To disable one of them, disable it and
# every module beneath it.
# -> This should not be strictly necessary anymore ()
code_locations.extend(
    [
        # "OpenStudioLandscapes.engine.compose_scopes.definitions",
        # "OpenStudioLandscapes.engine.landscape_map.definitions",
        # "OpenStudioLandscapes.engine.distributable.definitions",
    ]
)

modules = []


for core in code_locations:
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


# This loads the definitions from all the available (and
# enabled) Features.
# Todo:
#  - [ ] migrate to Code Locations
#        -> This is not so easy because "Materialize All" DOES NOT
#           work across multiple Code Locations
#        -> We can at least set the foundation for local Feature
#           development to function properly (`dagster dev --workspace <feature_workspace.yaml>`)
#        -> Because of this, we use the experimental `Definitions.merge()`
#           Feature to combine all individual Code Location into a single one
#           so that `workspace.yaml` only loads one Code Location
#        -> We can still deploy individual Code Locations and implement
#           testing etc.
#           -> Not true. The actual `AssetDefinition` clashes with
#              its related `AssetSpec`, raising
#              `dagster._core.errors.DagsterInvalidDefinitionError: Duplicate asset key: AssetKey(['OpenStudioLandscapes_Env', 'env'])`
#        References:
#        - https://stackoverflow.com/questions/79780791/dagster-multiple-code-locations-materialize-all-problem
#        - https://github.com/dagster-io/dagster/discussions/19184
#          - [Declarative Automation](https://docs.dagster.io/guides/automate/declarative-automation#declarative-automation)
#          - https://www.youtube.com/watch?v=Z77s50b_Sks
#        - https://github.com/dagster-io/dagster/discussions/19263
#        - https://www.youtube.com/watch?v=9U5OEQtDl-s
#        - https://github.com/dagster-io/dagster/issues/14422
defs = Definitions.merge(
    *[i.defs for i in modules],
)
