import importlib

from dagster import Definitions

from OpenStudioLandscapes.engine.constants import THIRD_PARTY

imports = [
    "OpenStudioLandscapes.engine.base.definitions",
    "OpenStudioLandscapes.engine.docker.definitions",
    "OpenStudioLandscapes.engine.landscape_map.definitions",
    "OpenStudioLandscapes.engine.compose.definitions",
    "OpenStudioLandscapes.engine.compose_worker.definitions",
    *[i["module"] for i in THIRD_PARTY if i["enabled"]],
]


modules = []

for module in imports:
    try:
        module_object = importlib.import_module(module)
        modules.append(module_object)
    except ModuleNotFoundError as e:
        print(e)
        raise e

defs = Definitions.merge(
    *[i.defs for i in modules],
)
