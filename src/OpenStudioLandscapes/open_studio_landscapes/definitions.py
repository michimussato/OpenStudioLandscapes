import importlib

from dagster import Definitions

from OpenStudioLandscapes.open_studio_landscapes.constants import THIRD_PARTY


imports = [
    "OpenStudioLandscapes.open_studio_landscapes.base.definitions",
    "OpenStudioLandscapes.open_studio_landscapes.compose.definitions",
    *THIRD_PARTY,
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
