import importlib

from dagster import Definitions, get_dagster_logger

from OpenStudioLandscapes.engine.discovery.discovery import IMPORTS

LOGGER = get_dagster_logger(__name__)

imports_engine = [
    "OpenStudioLandscapes.engine.base.definitions",
    "OpenStudioLandscapes.engine.env.definitions",
    "OpenStudioLandscapes.engine.compose_harbor.definitions",
    "OpenStudioLandscapes.engine.compose_pi_hole.definitions",
    "OpenStudioLandscapes.engine.compose_license_server.definitions",
    "OpenStudioLandscapes.engine.landscape_map.definitions",
    "OpenStudioLandscapes.engine.compose.definitions",
    "OpenStudioLandscapes.engine.compose_worker.definitions",
]


modules = []


for core in imports_engine:
    try:
        module_object = importlib.import_module(core)
        modules.append(module_object)
    except ModuleNotFoundError as e:
        LOGGER.error(f"Engine setup failed to complete: {e}")
        raise e


modules.extend(IMPORTS)


defs = Definitions.merge(
    *[i.defs for i in modules],
)
