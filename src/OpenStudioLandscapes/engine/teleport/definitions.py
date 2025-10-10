from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.teleport.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.teleport.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
