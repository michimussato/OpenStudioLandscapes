from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose.assets
import OpenStudioLandscapes.engine.compose.constants

assets = load_assets_from_modules(modules=[OpenStudioLandscapes.engine.compose.assets])
constants = load_assets_from_modules([OpenStudioLandscapes.engine.compose.constants])


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
