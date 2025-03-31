from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_harbor.assets
import OpenStudioLandscapes.engine.compose_harbor.constants

assets = load_assets_from_modules([OpenStudioLandscapes.engine.compose_harbor.assets])
constants = load_assets_from_modules([OpenStudioLandscapes.engine.compose_harbor.constants])


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
