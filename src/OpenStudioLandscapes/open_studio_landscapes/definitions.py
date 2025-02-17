import importlib

from dagster import Definitions

imports = [
    "OpenStudioLandscapes.open_studio_landscapes.base.definitions",
    "Ayon.definitions",
    "OpenStudioLandscapes_Dagster.definitions",
    "OpenStudioLandscapes_filebrowser.definitions",
    "OpenStudioLandscapes_Grafana.definitions",
    "OpenStudioLandscapes_Deadline_10_2.definitions",
    "LikeC4.definitions",
    "Kitsu.definitions",
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
