"""
This is the Feature discovery engine for OpenStudioLandscapes.
"""
__all__ = [
    "DISCOVERED_MODULE",
    "IMPORTABLE_FEATURES",
    "IMPORTED_FEATURES",
]

from setuptools import find_namespace_packages
import importlib

from dagster import get_dagster_logger

from OpenStudioLandscapes.engine.constants import THIRD_PARTY

LOGGER = get_dagster_logger(__name__)

namespace_packages = find_namespace_packages(where=".features", include=["*src.OpenStudioLandscapes.*"])

DISCOVERED_MODULE = [
    ".".join(
        [
            i.rsplit(".", 2)[-2],
            i.rsplit(".", 2)[-1],
            "definitions",
        ]
    ) for i in namespace_packages
]


IMPORTABLE_FEATURES = []


for feature in THIRD_PARTY:
    if feature["module"] not in DISCOVERED_MODULE:
        LOGGER.info("Feature %s is not in discovered modules. Skipped." % feature["module"])
        continue
    if not feature["enabled"]:
        LOGGER.info("Feature %s is not enabled. Skipped." % feature["module"])
        continue
    IMPORTABLE_FEATURES.append(feature)


IMPORTS = []  # used in definitions.py (list of <module> objects)
IMPORTED_FEATURES = []  # used in dynamic asset imports


for feature in IMPORTABLE_FEATURES:
    try:
        module_object = importlib.import_module(feature["module"])
        IMPORTS.append(module_object)
        IMPORTED_FEATURES.append(feature)
    except ModuleNotFoundError as e:
        LOGGER.warning(
            f"Feature {feature['module']} is enabled but import failed as it is not importable: {e}. "
            f"Did you forget to run "
            # f"`pip install -e ./.features/{str(feature['module'].rsplit('.', 1)[0]).replace('.', '-')}[dev]`?")
            f"`pip install -e ./.features/{str(feature['module'].rsplit('.', 1)[0]).replace('.', '-')}`?"
        )
