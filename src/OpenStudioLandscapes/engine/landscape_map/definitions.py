from typing import Dict

from dagster import (
    Definitions,
    load_assets_from_modules,
)

from OpenStudioLandscapes.engine.landscape_map import assets_external
import OpenStudioLandscapes.engine.landscape_map.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.landscape_map.assets],
)


defs = Definitions(
    assets=[
        *assets,
        *assets_external,
    ],
)
