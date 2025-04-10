import importlib

from dagster import Definitions

from OpenStudioLandscapes.engine.discovery.discovery import IMPORTS


imports_engine = [
    "OpenStudioLandscapes.engine.base.definitions",
    "OpenStudioLandscapes.engine.env.definitions",
    "OpenStudioLandscapes.engine.compose_harbor.definitions",
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
        print(e)
        raise e


modules.extend(IMPORTS)


defs = Definitions.merge(
    *[i.defs for i in modules],
)
