__all__ = [
    "DISCOVERED_MODULE",
    "IMPORTABLE_FEATURES",
    # "IMPORTS",
    "IMPORTED_FEATURES",
]

from setuptools import find_namespace_packages
import importlib

from OpenStudioLandscapes.engine.constants import THIRD_PARTY

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
        print(f"Feature {feature['module']} is not in discovered modules. Skipped.")
        continue
    if not feature["enabled"]:
        print(f"Feature {feature['module']} is not enabled. Skipped.")
        continue
    IMPORTABLE_FEATURES.append(feature)


IMPORTS = []
IMPORTED_FEATURES = []


for feature in IMPORTABLE_FEATURES:
    try:
        module_object = importlib.import_module(feature["module"])
        IMPORTS.append(module_object)
        IMPORTED_FEATURES.append(feature)
    except ModuleNotFoundError as e:
        print(f"Import of {feature['module']} failed as it is not importable ({e})")
        # raise e