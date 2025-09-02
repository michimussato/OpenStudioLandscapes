from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.constants
import OpenStudioLandscapes.engine.env.assets

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.env.assets])
constants = load_assets_from_modules([OpenStudioLandscapes.engine.constants])


defs = Definitions(
    assets=[
        *assets_base,
        *constants,
    ],
)
