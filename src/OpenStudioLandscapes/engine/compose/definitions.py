from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.compose.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
