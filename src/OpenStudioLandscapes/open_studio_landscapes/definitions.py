import importlib

from dagster import Definitions

IMPORTS = [
    "OpenStudioLandscapes_Ayon.definitions",
    "OpenStudioLandscapes_Dagster.definitions",
    "OpenStudioLandscapes_filebrowser.definitions",
    "OpenStudioLandscapes_Grafana.definitions",
    "OpenStudioLandscapes_Deadline_10_2.definitions",
    "OpenStudioLandscapes_LikeC4.definitions",
    "OpenStudioLandscapes_Kitsu.definitions",
]


imports_with_base = [
    "OpenStudioLandscapes.open_studio_landscapes.base.definitions",
    "OpenStudioLandscapes.open_studio_landscapes.compose.definitions",
    *IMPORTS,
]


modules = []

for module in imports_with_base:
    try:
        module_object = importlib.import_module(module)
        modules.append(module_object)
    except ModuleNotFoundError as e:
        print(e)
        raise e

defs = Definitions.merge(
    *[i.defs for i in modules],
)
