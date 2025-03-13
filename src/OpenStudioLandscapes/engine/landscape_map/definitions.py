from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.landscape_map.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.landscape_map.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
