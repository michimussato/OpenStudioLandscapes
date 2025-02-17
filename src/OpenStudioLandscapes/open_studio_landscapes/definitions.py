import importlib

from dagster import Definitions

imports = [
    "OpenStudioLandscapes.open_studio_landscapes.base.definitions",
    "OpenStudioLandscapes.open_studio_landscapes.compose.definitions",
    "OpenStudioLandscapes_Ayon.definitions",
    "OpenStudioLandscapes_Dagster.definitions",
    "OpenStudioLandscapes_filebrowser.definitions",
    "OpenStudioLandscapes_Grafana.definitions",
    "OpenStudioLandscapes_Deadline_10_2.definitions",
    # "OpenStudioLandscapes_LikeC4.definitions",
    "OpenStudioLandscapes_Kitsu.definitions",
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
